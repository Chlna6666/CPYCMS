# -*- coding: utf-8 -*-
"""CPYCMS - 账号应用配置。"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.accounts'
    label = 'accounts'
