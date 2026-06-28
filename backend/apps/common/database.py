# -*- coding: utf-8 -*-
"""CPYCMS - Django SQLite 初始化与连接优化。"""

from pathlib import Path
import shutil
import sqlite3
import time

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.db.backends.signals import connection_created


def configure_sqlite(sender, connection, **_kwargs):
    """为每个 SQLite 连接设置 PRAGMA。"""
    if connection.vendor != 'sqlite':
        return
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.execute(f'PRAGMA busy_timeout={int(settings.DATABASES["default"]["OPTIONS"].get("timeout", 5) * 1000)}')
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA temp_store=MEMORY')
        cursor.execute(f'PRAGMA cache_size=-{settings.SQLITE_CACHE_KB}')


connection_created.connect(configure_sqlite)


def database_path():
    """返回当前 SQLite 数据库路径。"""
    name = str(settings.DATABASES['default']['NAME'])
    if name == ':memory:' or name.startswith('file:'):
        return None
    return Path(name)


def _table_names(path):
    """以只读方式读取 SQLite 表名，避免检查动作创建数据库文件。"""
    if not path or not path.exists():
        return set()
    uri = f'file:{path.as_posix()}?mode=ro'
    with sqlite3.connect(uri, uri=True) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


def django_schema_ready():
    """判断 Django 迁移表和自定义用户表是否存在。"""
    path = database_path()
    if path is None:
        return True
    try:
        tables = _table_names(path)
    except sqlite3.DatabaseError:
        return False
    return 'django_migrations' in tables and 'accounts_user' in tables


def table_exists(table_name):
    """以只读方式判断指定表是否存在，避免检查动作创建空数据库。"""
    path = database_path()
    if path is None:
        return True
    try:
        return table_name in _table_names(path)
    except sqlite3.DatabaseError:
        return False


def backup_legacy_database():
    """发现旧 Flask 数据库时先重命名备份，避免 Django migration 冲突。"""
    path = database_path()
    if path is None or not path.exists():
        return None
    try:
        tables = _table_names(path)
    except sqlite3.DatabaseError:
        tables = {'legacy'}
    if not tables or 'django_migrations' in tables:
        return None

    stamp = time.strftime('%Y%m%d%H%M%S')
    backup = path.with_name(f'{path.stem}.flask-backup-{stamp}{path.suffix}')
    try:
        shutil.move(str(path), str(backup))
    except PermissionError as exc:
        if backup.exists():
            backup.unlink()
        raise RuntimeError('SQLite 数据库文件被占用，请关闭旧后端进程或数据库查看器后重试迁移') from exc
    for suffix in ('-wal', '-shm'):
        sidecar = Path(str(path) + suffix)
        if sidecar.exists():
            shutil.move(str(sidecar), str(backup) + suffix)
    return backup


def switch_to_fallback_database():
    """旧库被占用时切换到新的 Django 数据库文件。"""
    path = database_path()
    if path is None:
        raise RuntimeError('当前数据库配置无法切换到兜底文件')
    fallback = path.with_name(f'{path.stem}-django{path.suffix}')
    settings.DATABASES['default']['NAME'] = str(fallback)
    connections.databases['default']['NAME'] = str(fallback)
    connections.settings['default']['NAME'] = str(fallback)
    connections.close_all()
    return fallback


def ensure_database_schema(allow_fallback=False):
    """确保数据库结构存在，初始化提交时可从空库自动创建表。"""
    path = database_path()
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        backup_legacy_database()
    except RuntimeError:
        if not allow_fallback:
            raise
        fallback = switch_to_fallback_database()
        fallback.parent.mkdir(parents=True, exist_ok=True)
    call_command('migrate', interactive=False, verbosity=0)
