#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CPYCMS - Django 管理入口。"""

import os
import sys


def main():
    """运行 Django 命令行工具。"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')
    from django.core.management import execute_from_command_line
    if len(sys.argv) > 1 and sys.argv[1] == 'migrate':
        from backend.apps.common.database import backup_legacy_database, switch_to_fallback_database

        try:
            backup_legacy_database()
        except RuntimeError as exc:
            fallback = switch_to_fallback_database()
            print(f'{exc}；已改用新的 Django 数据库文件: {fallback}', file=sys.stderr)

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
