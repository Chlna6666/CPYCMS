# -*- coding: utf-8 -*-
"""CPYCMS - DRF 认证增强。"""

import logging

from django.db import OperationalError, ProgrammingError
from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication

from backend.apps.common.csrf import DynamicCsrfViewMiddleware
from backend.apps.common.database import table_exists
from backend.apps.common.session_security import clear_session_cookie, session_binding_valid


logger = logging.getLogger('cpycms.csrf')


class DynamicCSRFCheck(DynamicCsrfViewMiddleware):
    """DRF SessionAuthentication 使用的动态 CSRF 检查器。"""

    def _reject(self, request, reason):
        return reason


class SafeSessionAuthentication(SessionAuthentication):
    """数据库尚未初始化时安全跳过 Session 认证。

    删除 SQLite 后浏览器可能仍携带旧 sessionid Cookie。默认 SessionAuthentication
    会在视图执行前查询 django_session 表，导致初始化接口还没迁移就 500。
    """

    def authenticate(self, request):
        if not table_exists('django_session'):
            return None
        try:
            result = super().authenticate(request)
        except (OperationalError, ProgrammingError):
            return None
        if not result:
            return None
        user, _auth = result
        if user.is_authenticated and not session_binding_valid(request):
            logger.warning(
                'session binding rejected path=%s user_id=%s ip=%s ua=%s',
                getattr(request, 'path', '-'),
                getattr(user, 'id', '-'),
                request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '-')).split(',')[0].strip(),
                request.META.get('HTTP_USER_AGENT', '')[:120],
            )
            clear_session_cookie(request)
            return None
        return result

    def enforce_csrf(self, request):
        """使用绑定域名缓存执行 CSRF 校验。"""

        def dummy_get_response(_request):
            return None

        check = DynamicCSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            logger.warning(
                'csrf rejected path=%s reason=%s host=%s forwarded_host=%s forwarded_proto=%s origin=%s referer=%s fetch_site=%s',
                getattr(request, 'path', '-'),
                reason,
                request.META.get('HTTP_HOST', ''),
                request.META.get('HTTP_X_FORWARDED_HOST', ''),
                request.META.get('HTTP_X_FORWARDED_PROTO', ''),
                request.META.get('HTTP_ORIGIN', ''),
                request.META.get('HTTP_REFERER', ''),
                request.META.get('HTTP_SEC_FETCH_SITE', ''),
            )
            raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')
