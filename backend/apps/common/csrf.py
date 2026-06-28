# -*- coding: utf-8 -*-
"""CPYCMS - 支持数据库绑定域名的 CSRF 中间件。"""

import logging
from urllib.parse import urlsplit

from django.core.exceptions import DisallowedHost
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.http import is_same_domain

from backend.apps.common.site_runtime import get_csrf_trusted_hosts_cached, get_csrf_trusted_origins_cached


logger = logging.getLogger('cpycms.csrf')


def canonical_netloc(netloc, scheme=''):
    """规范化 host[:port]，避免 HTTPS 反代默认端口导致同源误判。"""
    try:
        parsed = urlsplit(f'//{netloc}')
    except ValueError:
        return ''
    host = (parsed.hostname or '').lower()
    if not host:
        return ''
    port = parsed.port
    if (scheme == 'https' and port == 443) or (scheme == 'http' and port == 80) or (not scheme and port in {80, 443}):
        port = None
    return f'{host}:{port}' if port else host


def canonical_origin(value):
    """规范化 Origin/Referer 为 scheme://host[:port]。"""
    try:
        parsed = urlsplit(value or '')
    except ValueError:
        return ''
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        return ''
    host = canonical_netloc(parsed.netloc, parsed.scheme)
    return f'{parsed.scheme}://{host}' if host else ''


class DynamicCsrfViewMiddleware(CsrfViewMiddleware):
    """在 Django CSRF 白名单之外，额外信任后台持久化的绑定域名。"""

    def _reject(self, request, reason):
        """记录全局 CSRF 拒绝原因，不输出 Cookie 或 token。"""
        logger.warning(
            'csrf rejected path=%s reason=%s host=%s forwarded_host=%s forwarded_proto=%s origin=%s referer=%s fetch_site=%s ip=%s',
            getattr(request, 'path', '-'),
            reason,
            request.META.get('HTTP_HOST', ''),
            request.META.get('HTTP_X_FORWARDED_HOST', ''),
            request.META.get('HTTP_X_FORWARDED_PROTO', ''),
            request.META.get('HTTP_ORIGIN', ''),
            request.META.get('HTTP_REFERER', ''),
            request.META.get('HTTP_SEC_FETCH_SITE', ''),
            request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '-')).split(',')[0].strip(),
        )
        return super()._reject(request, reason)

    def _origin_verified(self, request):
        if super()._origin_verified(request):
            return True
        request_origin = request.META.get('HTTP_ORIGIN', '')
        if request_origin in get_csrf_trusted_origins_cached():
            return True
        if self._same_https_host_origin(request, request_origin):
            return True
        return self._browser_same_origin_verified(request, request_origin)

    def _same_https_host_origin(self, request, request_origin):
        """允许 HTTPS 反向代理场景下的同主机 Origin。

        浏览器看到的是 https://example.com，Django 容器内部可能只看到
        http://example.com。该分支只放行 HTTPS Origin 且 host 完全一致的
        情况，不放宽跨域请求。
        """
        try:
            origin = urlsplit(request_origin or '')
        except ValueError:
            return False
        if origin.scheme != 'https' or not origin.netloc:
            return False
        try:
            request_host = request.get_host()
        except DisallowedHost:
            return False
        return canonical_netloc(origin.netloc, origin.scheme) == canonical_netloc(request_host)

    def _browser_same_origin_verified(self, request, request_origin):
        """使用现代浏览器 Fetch Metadata 兜底识别真实同源请求。

        部分 OpenResty/边缘节点转发到容器时没有保留 Host/X-Forwarded-Host，
        Django 只能看到内部地址，传统 Origin-vs-Host 校验会失败。浏览器
        自动发送的 Sec-Fetch-Site 无法被网页脚本伪造；当它声明 same-origin，
        且 Origin 与 Referer 本身同源时，可判定这是浏览器视角下的同源请求。
        """
        if request.META.get('HTTP_SEC_FETCH_SITE') != 'same-origin':
            return False
        origin = canonical_origin(request_origin)
        referer = canonical_origin(request.META.get('HTTP_REFERER', ''))
        return bool(origin and referer and origin == referer)

    def _check_referer(self, request):
        try:
            return super()._check_referer(request)
        except Exception as exc:
            referer = request.META.get('HTTP_REFERER')
            try:
                parsed = urlsplit(referer or '')
            except ValueError:
                raise exc
            try:
                request_host = request.get_host()
            except DisallowedHost:
                request_host = ''
            if parsed.scheme == 'https' and canonical_netloc(parsed.netloc, parsed.scheme) == canonical_netloc(request_host):
                return None
            if parsed.scheme == 'https' and any(is_same_domain(parsed.netloc.lower(), host) for host in get_csrf_trusted_hosts_cached()):
                return None
            if request.META.get('HTTP_SEC_FETCH_SITE') == 'same-origin' and canonical_origin(referer):
                return None
            raise exc
