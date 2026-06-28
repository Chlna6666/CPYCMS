# -*- coding: utf-8 -*-
"""CPYCMS - 公共基础能力应用配置。"""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.common'
    label = 'common'

    def ready(self):
        """注册 SQLite 连接级优化和日志系统。"""
        from backend.apps.common import database  # noqa: F401
        from backend.apps.common.logging import configure_logging

        configure_logging()
