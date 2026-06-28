# -*- coding: utf-8 -*-
"""CPYCMS - Gunicorn 生产运行配置。"""

import os


def _env_int(name, default, min_value=1, max_value=None):
    """读取整数环境变量并限制范围。"""
    try:
        value = int(os.environ.get(name) or default)
    except (TypeError, ValueError):
        value = default
    value = max(min_value, value)
    return min(value, max_value) if max_value is not None else value


def _cpu_count():
    """返回可用 CPU 数。"""
    return max(1, os.cpu_count() or 1)


bind = f"0.0.0.0:{os.environ.get('CPYCMS_PORT', '5000')}"
workers = _env_int('GUNICORN_WORKERS', min(max(_cpu_count(), 2), 3), 1, 8)
threads = _env_int('GUNICORN_THREADS', min(max(_cpu_count() * 2, 4), 12), 1, 32)
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'gthread')
timeout = _env_int('GUNICORN_TIMEOUT', 120, 10, 600)
keepalive = _env_int('GUNICORN_KEEPALIVE', 5, 1, 120)
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')
loglevel = os.environ.get('CPYCMS_LOG_LEVEL', 'info').lower()
capture_output = True
enable_stdio_inheritance = True


def when_ready(server):
    """Gunicorn 启动完成后输出最终并发配置。"""
    server.log.info(
        'CPYCMS Gunicorn ready workers=%s threads=%s worker_class=%s timeout=%s',
        workers,
        threads,
        worker_class,
        timeout,
    )
