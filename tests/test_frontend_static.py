# -*- coding: utf-8 -*-
"""CPYCMS 前端静态资源与 SPA fallback 测试。"""

import pytest
from django.test import override_settings


pytestmark = pytest.mark.django_db


def response_body(response) -> bytes:
    """兼容普通响应和 FileResponse 的测试读取方式。"""
    if getattr(response, 'streaming', False):
        return b''.join(response.streaming_content)
    return response.content


@override_settings(DEBUG=False, USE_VITE_DEV_SERVER=False)
def test_dist_module_assets_do_not_fall_back_to_html(client, settings, tmp_path):
    """正式资源请求应返回真实 JS/MJS 内容，而不是 index.html。"""
    settings.FRONTEND_DIST = tmp_path
    assets_dir = tmp_path / 'assets'
    vendor_dir = tmp_path / 'vendor' / 'demo'
    assets_dir.mkdir(parents=True)
    vendor_dir.mkdir(parents=True)
    (tmp_path / 'index.html').write_text('<div id="app"></div>', encoding='utf-8')
    (assets_dir / 'app.js').write_text('export default 1', encoding='utf-8')
    (vendor_dir / 'tool.mjs').write_text('export const ok = true', encoding='utf-8')

    js_response = client.get('/assets/app.js')
    mjs_response = client.get('/vendor/demo/tool.mjs')

    assert js_response.status_code == 200
    assert 'text/html' not in js_response['Content-Type']
    assert response_body(js_response) == b'export default 1'
    assert mjs_response.status_code == 200
    assert 'text/html' not in mjs_response['Content-Type']
    assert response_body(mjs_response) == b'export const ok = true'


@override_settings(DEBUG=False, USE_VITE_DEV_SERVER=False)
def test_missing_dist_asset_returns_plain_404(client, settings, tmp_path):
    """缺失 chunk 不应返回 SPA HTML，避免浏览器报错误导性的 MIME 问题。"""
    settings.FRONTEND_DIST = tmp_path
    (tmp_path / 'index.html').write_text('<div id="app"></div>', encoding='utf-8')

    response = client.get('/assets/missing.js')

    assert response.status_code == 404
    assert response['Content-Type'].startswith('text/plain')
    assert b'<div id="app">' not in response.content


@override_settings(DEBUG=False, USE_VITE_DEV_SERVER=False)
def test_spa_route_returns_dist_index(client, settings, tmp_path):
    """正式环境前端 history 路由应回退到 index.html。"""
    settings.FRONTEND_DIST = tmp_path
    (tmp_path / 'index.html').write_text('<div id="app">CPYCMS</div>', encoding='utf-8')

    response = client.get('/portfolio')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/html')
    assert b'CPYCMS' in response_body(response)


@override_settings(DEBUG=True, USE_VITE_DEV_SERVER=True, FRONTEND_DEV_SERVER_URL='http://vite.local:5173')
def test_dev_frontend_route_proxies_to_vite(client, monkeypatch):
    """开发模式下 Vue 源码模块应代理到 Vite，而不是依赖 frontend/dist。"""
    from backend.apps.common import frontend

    class FakeUpstream:
        status = 200
        headers = {'Content-Type': 'application/javascript', 'Cache-Control': 'no-cache'}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b'console.log("vite")'

    captured = {}

    def fake_urlopen(request, timeout):
        captured['url'] = request.full_url
        return FakeUpstream()

    monkeypatch.setattr(frontend, 'urlopen', fake_urlopen)

    response = client.get('/src/main.ts?t=1')

    assert captured['url'] == 'http://vite.local:5173/src/main.ts?t=1'
    assert response.status_code == 200
    assert response['Content-Type'].startswith('application/javascript')
    assert response.content == b'console.log("vite")'
