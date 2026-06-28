# -*- coding: utf-8 -*-
"""CPYCMS - 用户序列化。"""


def user_dict(user):
    """管理员用户序列化。"""
    return {
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'email': user.email,
        'avatar': user.avatar,
        'bio': user.bio,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'is_admin': bool(user.is_active and (user.is_staff or user.is_superuser)),
        'created_at': user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
        'updated_at': '',
    }
