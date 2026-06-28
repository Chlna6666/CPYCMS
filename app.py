# -*- coding: utf-8 -*-
"""CPYCMS - Django 本地开发入口。

PyCharm 直接运行本文件时，会启动 Django runserver；正式部署请使用
``python manage.py migrate`` 后通过 Gunicorn 加载 ``wsgi:application``。
"""

import os
import sys


def main():
    """启动 Django 开发服务器。"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')
    os.environ.setdefault('CPYCMS_DEBUG', '1')
    import django
    from django.core.management import execute_from_command_line
    from backend.apps.common.database import ensure_database_schema
    from backend.apps.common.frontend import start_vite_dev_server
    from backend.apps.common.site_runtime import refresh_site_runtime_cache

    django.setup()
    ensure_database_schema()
    refresh_site_runtime_cache()
    start_vite_dev_server()

    host = os.environ.get('CPYCMS_HOST', '0.0.0.0')
    port = os.environ.get('CPYCMS_PORT', '5000')
    args = [sys.argv[0], 'runserver', f'{host}:{port}']
    execute_from_command_line(args)


if __name__ == '__main__':
    main()
