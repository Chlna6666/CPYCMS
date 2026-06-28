# -*- coding: utf-8 -*-
"""CPYCMS - 管理员会话安全工具。"""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import time

from django.conf import settings


SESSION_BINDING_KEY = '_cpycms_session_binding'
SESSION_ISSUED_AT_KEY = '_cpycms_session_issued_at'


def _django_request(request):
    """兼容 DRF Request 和 Django HttpRequest。"""
    return getattr(request, '_request', request)


def _header(request, name, limit=300):
    """读取并截断请求头，避免把超长头写入哈希输入。"""
    return str(request.META.get(name, '') or '').strip()[:limit]


def _client_ip_prefix(request):
    """返回客户端 IP 的粗粒度网段，降低公网 IP 小范围变化造成的误判。"""
    forwarded = _header(request, 'HTTP_X_FORWARDED_FOR', 200)
    raw_ip = forwarded.split(',')[0].strip() if forwarded else _header(request, 'REMOTE_ADDR', 80)
    try:
        ip = ipaddress.ip_address(raw_ip)
    except ValueError:
        return ''
    if ip.version == 4:
        parts = raw_ip.split('.')
        return '.'.join(parts[:3]) if len(parts) == 4 else raw_ip
    return ':'.join(ip.exploded.split(':')[:4])


def _session_binding_source(request):
    """构造稳定的客户端特征源，默认不绑定 IP 以减少误登出。"""
    request = _django_request(request)
    parts = [
        _header(request, 'HTTP_USER_AGENT', 500),
        _header(request, 'HTTP_ACCEPT_LANGUAGE', 120),
        _header(request, 'HTTP_SEC_CH_UA_PLATFORM', 80),
    ]
    if getattr(settings, 'CPYCMS_SESSION_BIND_IP', False):
        parts.append(_client_ip_prefix(request))
    return '\n'.join(parts)


def build_session_binding(request):
    """使用服务端密钥生成不可伪造的会话绑定摘要。"""
    source = _session_binding_source(request).encode('utf-8', errors='ignore')
    key = str(settings.SECRET_KEY).encode('utf-8', errors='ignore')
    return hmac.new(key, source, hashlib.sha256).hexdigest()


def bind_session_to_request(request):
    """登录成功后写入服务端 session 绑定信息。"""
    request = _django_request(request)
    request.session[SESSION_BINDING_KEY] = build_session_binding(request)
    request.session[SESSION_ISSUED_AT_KEY] = int(time.time())
    request.session.modified = True


def session_binding_valid(request):
    """校验当前已认证 session 是否由同一客户端上下文创建。"""
    request = _django_request(request)
    stored = request.session.get(SESSION_BINDING_KEY)
    if not stored:
        return False
    return hmac.compare_digest(str(stored), build_session_binding(request))


def clear_session_cookie(request):
    """清理伪造、过期或缺少绑定信息的 session。"""
    request = _django_request(request)
    try:
        request.session.flush()
    except Exception:
        request.session.clear()
        request.session.modified = True
