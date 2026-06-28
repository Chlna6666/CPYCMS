# -*- coding: utf-8 -*-
"""CPYCMS - 站点运行时配置缓存。"""

from __future__ import annotations

import threading
from urllib.parse import urlsplit

from django.conf import settings
from django.db import OperationalError, ProgrammingError

from backend.apps.common.database import table_exists
from backend.apps.common.settings_defaults import DEFAULT_SITE_SETTINGS


_runtime_lock = threading.RLock()
_settings_cache: dict[str, str] | None = None
_trusted_origins: set[str] = set()
_trusted_hosts: set[str] = set()


def _normalize_origin(value: str) -> str:
    """规范化绑定域名，返回 scheme://host[:port]。"""
    raw = str(value or '').strip().strip('/')
    if not raw:
        return ''
    if raw.lower().startswith(('javascript:', 'data:', 'file:')):
        return ''
    if '://' not in raw:
        raw = f'https://{raw}'
    parsed = urlsplit(raw)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        return ''
    return f'{parsed.scheme}://{parsed.netloc.lower()}'


def parse_bound_origins(value: str) -> set[str]:
    """解析逗号、换行分隔的绑定域名列表。"""
    origins: set[str] = set()
    for item in str(value or '').replace('\n', ',').split(','):
        origin = _normalize_origin(item)
        if origin:
            origins.add(origin)
    return origins


def _origin_hosts(origins: set[str]) -> set[str]:
    """从 origin 集合提取 host[:port]。"""
    hosts = set()
    for origin in origins:
        parsed = urlsplit(origin)
        if parsed.netloc:
            hosts.add(parsed.netloc.lstrip('*').lower())
    return hosts


def _origins_from_allowed_hosts() -> set[str]:
    """把明确的 ALLOWED_HOSTS 补充为 HTTPS 可信源。"""
    origins: set[str] = set()
    for host in getattr(settings, 'ALLOWED_HOSTS', []):
        value = str(host or '').strip()
        if not value or '*' in value or value.startswith('.'):
            continue
        origin = _normalize_origin(value)
        if origin:
            origins.add(origin)
    return origins


def _load_settings_from_db() -> dict[str, str]:
    """读取站点设置表；表不存在时返回默认配置。"""
    if not table_exists('site_settings'):
        return dict(DEFAULT_SITE_SETTINGS)
    try:
        from backend.apps.cms.models import SiteSetting

        current = {item.key: item.value for item in SiteSetting.objects.all()}
    except (OperationalError, ProgrammingError):
        current = {}
    merged = dict(DEFAULT_SITE_SETTINGS)
    merged.update(current)
    return merged


def refresh_site_runtime_cache() -> dict[str, str]:
    """刷新内存中的站点配置和 CSRF 可信源缓存。"""
    global _settings_cache, _trusted_hosts, _trusted_origins
    loaded = _load_settings_from_db()
    bound_origins = parse_bound_origins(loaded.get('bound_domains', ''))
    env_origins = {origin for origin in settings.CSRF_TRUSTED_ORIGINS if origin}
    host_origins = _origins_from_allowed_hosts()
    with _runtime_lock:
        _settings_cache = loaded
        _trusted_origins = env_origins | bound_origins | host_origins
        _trusted_hosts = _origin_hosts(_trusted_origins)
    return dict(loaded)


def get_site_settings_cached() -> dict[str, str]:
    """读取缓存的站点配置，首次访问时懒加载。"""
    with _runtime_lock:
        if _settings_cache is not None:
            return dict(_settings_cache)
    return refresh_site_runtime_cache()


def get_csrf_trusted_origins_cached() -> set[str]:
    """返回内存缓存的 CSRF 可信 origin。"""
    get_site_settings_cached()
    with _runtime_lock:
        return set(_trusted_origins)


def get_csrf_trusted_hosts_cached() -> set[str]:
    """返回内存缓存的 CSRF 可信 host。"""
    get_site_settings_cached()
    with _runtime_lock:
        return set(_trusted_hosts)
