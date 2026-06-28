# -*- coding: utf-8 -*-
"""CPYCMS - CMS 应用配置。"""

from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.cms'
    label = 'cms'
