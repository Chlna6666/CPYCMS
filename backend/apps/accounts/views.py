# -*- coding: utf-8 -*-
"""CPYCMS - 认证 API。"""

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from backend.apps.accounts.serializers import user_dict
from backend.apps.common.permissions import admin_required
from backend.apps.common.session_security import bind_session_to_request


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token(request):
    """设置 CSRF cookie。"""
    return Response({'detail': 'CSRF cookie set'})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """管理员登录。"""
    username = str(request.data.get('username') or '').strip()
    password = str(request.data.get('password') or '').strip()
    if not username or not password:
        return Response({'detail': '请输入用户名和密码'}, status=400)
    user = authenticate(request, username=username, password=password)
    if not user or not user.is_active:
        return Response({'detail': '用户名或密码错误'}, status=401)
    if not (user.is_staff or user.is_superuser):
        return Response({'detail': '当前账号没有后台管理权限'}, status=403)
    login(request, user)
    bind_session_to_request(request)
    return Response(user_dict(user))


@api_view(['POST'])
@admin_required
def logout_view(request):
    """退出登录。"""
    logout(request)
    return Response({'detail': '已退出登录'})


@api_view(['GET'])
@permission_classes([AllowAny])
def session_view(request):
    """检查当前登录状态。"""
    if not request.user.is_authenticated:
        return Response({'logged_in': False})
    return Response({'logged_in': True, 'user': user_dict(request.user)})


@api_view(['PUT'])
@admin_required
def profile_view(request):
    """修改个人资料。"""
    user = request.user
    user.nickname = str(request.data.get('nickname', user.nickname) or '')[:80]
    user.email = str(request.data.get('email', user.email) or '')[:120]
    user.avatar = str(request.data.get('avatar', user.avatar) or '')[:256]
    user.bio = str(request.data.get('bio', user.bio) or '')
    user.save(update_fields=['nickname', 'email', 'avatar', 'bio'])
    return Response(user_dict(user))


@api_view(['PUT'])
@admin_required
def password_view(request):
    """修改密码。"""
    old_password = str(request.data.get('old_password') or '')
    new_password = str(request.data.get('new_password') or '')
    if not request.user.check_password(old_password):
        return Response({'detail': '当前密码错误'}, status=400)
    if len(new_password) < 6:
        return Response({'detail': '新密码至少6个字符'}, status=400)
    request.user.set_password(new_password)
    request.user.save(update_fields=['password'])
    login(request, request.user)
    bind_session_to_request(request)
    return Response({'detail': '密码修改成功'})
