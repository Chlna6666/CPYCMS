# -*- coding: utf-8 -*-
"""CPYCMS - API 权限辅助。"""

from functools import wraps

from rest_framework.response import Response


def admin_required(view_func):
    """要求已登录管理员。"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': '未登录'}, status=401)
        if not request.user.is_active:
            return Response({'detail': '账号已禁用'}, status=403)
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'detail': '当前账号没有后台管理权限'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
