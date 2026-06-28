# -*- coding: utf-8 -*-
"""CPYCMS - 前端开发代理与正式静态资源服务。"""

from __future__ import annotations

import atexit
import mimetypes
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.utils._os import safe_join
from django.core.exceptions import SuspiciousFileOperation


mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('text/javascript', '.mjs')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('image/svg+xml', '.svg')

_vite_process: subprocess.Popen | None = None
_HOP_BY_HOP_HEADERS = {
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailer',
    'transfer-encoding',
    'upgrade',
    'host',
    'content-length',
}


def use_vite_dev_server() -> bool:
    """判断当前请求是否应交给 Vite 开发服务器。"""
    return bool(getattr(settings, 'USE_VITE_DEV_SERVER', False))


def _frontend_url() -> str:
    """返回规范化后的 Vite 开发服务器地址。"""
    return str(settings.FRONTEND_DEV_SERVER_URL).rstrip('/')


def _server_reachable(url: str, timeout: float = 0.6) -> bool:
    """探测 Vite 是否已经可访问。"""
    try:
        with urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 500
    except (OSError, URLError):
        return False


def _vite_env() -> dict[str, str]:
    """为 Vite 子进程注入与 Django 端口一致的开发环境变量。"""
    parsed = urlparse(_frontend_url())
    env = os.environ.copy()
    if parsed.hostname:
        env.setdefault('VITE_DEV_HOST', parsed.hostname)
    if parsed.port:
        env.setdefault('VITE_DEV_PORT', str(parsed.port))
    backend_port = os.environ.get('CPYCMS_PORT', '5000')
    env.setdefault('VITE_BACKEND_URL', f'http://127.0.0.1:{backend_port}')
    return env


def _npm_executable() -> str:
    """返回当前系统可执行的 npm 命令名。"""
    return 'npm.cmd' if os.name == 'nt' else 'npm'


def _stop_vite_process() -> None:
    """退出 Django 开发进程时尽量回收自动启动的 Vite 进程树。"""
    global _vite_process
    process = _vite_process
    if process is None or process.poll() is not None:
        return
    try:
        if os.name == 'nt':
            subprocess.run(
                ['taskkill', '/PID', str(process.pid), '/T', '/F'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            process.terminate()
            process.wait(timeout=5)
    except Exception:
        process.kill()
    finally:
        _vite_process = None


def start_vite_dev_server() -> None:
    """在开发模式下启动 Vite，并把 Vite 日志直接输出到当前控制台。"""
    global _vite_process
    if not use_vite_dev_server() or not getattr(settings, 'AUTO_START_VITE', False):
        return

    # Django autoreload 会创建父/子进程；只在父进程启动 Vite，避免重复占用端口。
    if os.environ.get('RUN_MAIN') == 'true':
        return

    frontend_url = _frontend_url()
    if _server_reachable(frontend_url):
        print(f'[CPYCMS] Vite dev server is already running: {frontend_url}', flush=True)
        return

    frontend_dir = Path(settings.FRONTEND_DIR)
    if not (frontend_dir / 'package.json').exists():
        print(f'[CPYCMS] frontend package.json not found: {frontend_dir}', file=sys.stderr, flush=True)
        return

    command = [_npm_executable(), 'run', 'dev']
    print(f'[CPYCMS] starting Vite dev server: {" ".join(command)}', flush=True)
    try:
        _vite_process = subprocess.Popen(
            command,
            cwd=str(frontend_dir),
            env=_vite_env(),
            stdout=None,
            stderr=None,
        )
    except OSError as exc:
        print(f'[CPYCMS] failed to start Vite dev server: {exc}', file=sys.stderr, flush=True)
        return

    atexit.register(_stop_vite_process)
    deadline = time.monotonic() + settings.VITE_STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        if _server_reachable(frontend_url):
            print(f'[CPYCMS] Vite dev server ready: {frontend_url}', flush=True)
            return
        if _vite_process.poll() is not None:
            print('[CPYCMS] Vite dev server exited during startup', file=sys.stderr, flush=True)
            return
        time.sleep(0.3)
    print(f'[CPYCMS] Vite dev server startup timed out: {frontend_url}', file=sys.stderr, flush=True)


def _proxy_headers(request) -> dict[str, str]:
    """复制安全的请求头到 Vite，跳过逐跳头。"""
    return {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in _HOP_BY_HOP_HEADERS
    }


def _copy_response_headers(target: HttpResponse, source_headers) -> None:
    """复制 Vite 响应中的缓存与内容相关头。"""
    allowed = {'cache-control', 'etag', 'last-modified', 'vary'}
    for key, value in source_headers.items():
        if key.lower() in allowed:
            target[key] = value


def proxy_to_vite(request) -> HttpResponse:
    """将开发期前端页面、模块和 public 资源转发到 Vite。"""
    url = f'{_frontend_url()}{request.get_full_path()}'
    payload = request.body if request.method not in {'GET', 'HEAD'} else None
    upstream_request = Request(url, data=payload, headers=_proxy_headers(request), method=request.method)
    try:
        with urlopen(upstream_request, timeout=15) as upstream:
            body = b'' if request.method == 'HEAD' else upstream.read()
            response = HttpResponse(
                body,
                status=upstream.status,
                content_type=upstream.headers.get('Content-Type') or 'application/octet-stream',
            )
            _copy_response_headers(response, upstream.headers)
            return response
    except HTTPError as exc:
        body = b'' if request.method == 'HEAD' else exc.read()
        response = HttpResponse(
            body,
            status=exc.code,
            content_type=exc.headers.get('Content-Type') or 'text/plain; charset=utf-8',
        )
        _copy_response_headers(response, exc.headers)
        return response
    except (OSError, URLError):
        return HttpResponse(
            '前端开发服务器未启动或不可访问，请运行 python app.py 自动启动，或在 frontend 目录手动执行 npm run dev。',
            status=502,
            content_type='text/plain; charset=utf-8',
        )


def _dist_file(path: str) -> Path | None:
    """安全解析 frontend/dist 内的静态文件路径。"""
    try:
        full_path = Path(safe_join(str(settings.FRONTEND_DIST), path))
    except SuspiciousFileOperation:
        return None
    if not full_path.is_file():
        return None
    return full_path


def serve_dist_asset(_request, path: str) -> HttpResponse:
    """正式环境下返回真实静态资源，避免模块请求落到 HTML fallback。"""
    full_path = _dist_file(path)
    if full_path is None:
        return HttpResponse('static asset not found', status=404, content_type='text/plain; charset=utf-8')
    content_type = mimetypes.guess_type(str(full_path))[0] or 'application/octet-stream'
    return FileResponse(full_path.open('rb'), content_type=content_type)


def serve_spa_index(_request) -> HttpResponse:
    """正式环境下返回 Vue 单页应用入口。"""
    index_path = _dist_file('index.html')
    if index_path is None:
        raise Http404('frontend dist not found')
    return FileResponse(index_path.open('rb'), content_type='text/html')


def frontend_asset(request, path: str) -> HttpResponse:
    """开发期代理 Vite 资源，正式环境返回 dist 中的资源。"""
    if use_vite_dev_server():
        return proxy_to_vite(request)
    return serve_dist_asset(request, path)


def frontend_entry(request, path: str = '') -> HttpResponse:
    """开发期代理 Vite，正式环境返回 SPA fallback。"""
    if use_vite_dev_server():
        return proxy_to_vite(request)
    return serve_spa_index(request)
