# -*- coding: utf-8 -*-
"""CPYCMS - Django 日志配置工具。"""

import atexit
import ctypes
import gzip
import logging
import os
import queue
import shutil
import sys
import time
from contextlib import suppress
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from pathlib import Path


_listener = None
_RESET = '\033[0m'
_DIM = '\033[2m'
_LEVEL_COLORS = {
    logging.DEBUG: '\033[36m',
    logging.INFO: '\033[32m',
    logging.WARNING: '\033[33m',
    logging.ERROR: '\033[31m',
    logging.CRITICAL: '\033[1;41m',
}


class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """按天滚动、自动 gzip 压缩并按数量和总大小清理旧日志。"""

    def __init__(self, *args, max_total_mb=256, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_total_bytes = max_total_mb * 1024 * 1024

    def _warn_rotation_busy(self, source, exc=None):
        """轮转被 Windows 文件锁阻塞时只输出警告，不打断业务日志链路。"""
        reason = f': {exc}' if exc else ''
        with suppress(Exception):
            sys.stderr.write(f'[CPYCMS] log rotation skipped because file is busy: {source}{reason}\n')

    def _archive_path(self, gz_dest):
        """生成压缩归档路径，避免多进程同时轮转时互相覆盖。"""
        target = Path(gz_dest)
        if not target.exists():
            return target
        return target.with_name(f'{target.stem}.{os.getpid()}.{time.time_ns()}{target.suffix}')

    def rotate(self, source, dest):
        """滚动时将旧日志压缩成 .gz。"""
        if not os.path.exists(source):
            return
        gz_dest = dest if dest.endswith('.gz') else f'{dest}.gz'
        archive_path = self._archive_path(gz_dest)
        temp_path = archive_path.with_name(f'{archive_path.name}.tmp-{os.getpid()}')
        try:
            with open(source, 'rb') as src, gzip.open(temp_path, 'wb', compresslevel=6) as dst:
                shutil.copyfileobj(src, dst)
            os.replace(temp_path, archive_path)
        except OSError as exc:
            with suppress(OSError):
                temp_path.unlink()
            self._warn_rotation_busy(source, exc)
            return
        try:
            os.remove(source)
        except OSError as exc:
            self._warn_rotation_busy(source, exc)

    def getFilesToDelete(self):
        """返回需要删除的过期压缩日志文件。"""
        base_path = Path(self.baseFilename)
        prefix = base_path.name + '.'
        try:
            candidates = [
                item for item in base_path.parent.iterdir()
                if item.is_file() and item.name.startswith(prefix) and item.suffix == '.gz'
            ]
            candidates.sort(key=lambda item: item.stat().st_mtime)
        except OSError:
            return []
        files_to_delete = []
        if self.backupCount > 0 and len(candidates) > self.backupCount:
            files_to_delete.extend(candidates[:len(candidates) - self.backupCount])
            candidates = candidates[len(candidates) - self.backupCount:]

        total_size = sum(item.stat().st_size for item in candidates)
        while self.max_total_bytes > 0 and candidates and total_size > self.max_total_bytes:
            oldest = candidates.pop(0)
            files_to_delete.append(oldest)
            total_size -= oldest.stat().st_size
        return [str(item) for item in files_to_delete]


class ColorFormatter(logging.Formatter):
    """控制台彩色日志格式器。"""

    def format(self, record):
        rendered = super().format(record)
        color = _LEVEL_COLORS.get(record.levelno, '')
        return f'{color}{rendered}{_RESET}' if color else rendered


def _enable_windows_ansi(stream):
    """在 Windows 控制台启用 ANSI 输出。"""
    if os.name != 'nt':
        return True
    try:
        handle = ctypes.windll.kernel32.GetStdHandle(-11 if stream is sys.stdout else -12)
        mode = ctypes.c_uint32()
        if not ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(ctypes.windll.kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False


def supports_color(stream):
    """判断当前终端是否适合输出 ANSI 高亮。"""
    mode = os.environ.get('CPYCMS_LOG_COLOR', 'auto').lower()
    if mode in {'0', 'false', 'never', 'off'} or os.environ.get('NO_COLOR'):
        return False
    if mode in {'1', 'true', 'always', 'on'} or os.environ.get('FORCE_COLOR'):
        _enable_windows_ansi(stream)
        return True
    if not hasattr(stream, 'isatty') or not stream.isatty():
        return False
    if os.environ.get('TERM', '').lower() == 'dumb':
        return False
    return _enable_windows_ansi(stream) or os.name != 'nt'


def skip_file_logging_for_reloader_parent():
    """Django runserver 自动重载父进程只输出控制台日志，避免 Windows 双进程占用同一日志文件。"""
    is_runserver = any(arg == 'runserver' or arg.endswith('runserver') for arg in sys.argv)
    no_reload = '--noreload' in sys.argv
    return is_runserver and not no_reload and os.environ.get('RUN_MAIN') != 'true'


def configure_logging():
    """配置队列异步日志，降低请求线程写磁盘开销。"""
    global _listener
    if _listener is not None:
        return

    level_name = os.environ.get('CPYCMS_LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, level_name, logging.INFO)
    log_dir = Path(os.environ.get('CPYCMS_LOG_DIR', Path.cwd() / 'logs'))
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [pid=%(process)d thread=%(threadName)s] %(name)s: %(message)s'
    )
    console_fmt = (
        f'{_DIM}%(asctime)s{_RESET} %(levelname)s '
        f'{_DIM}[pid=%(process)d thread=%(threadName)s]{_RESET} %(name)s: %(message)s'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColorFormatter(console_fmt) if supports_color(sys.stdout) else formatter)

    listener_handlers = [console_handler]
    if not skip_file_logging_for_reloader_parent():
        file_handler = CompressedTimedRotatingFileHandler(
            str(log_dir / 'cpycms.log'),
            when='midnight',
            interval=1,
            backupCount=int(os.environ.get('CPYCMS_LOG_BACKUP_DAYS', '14')),
            encoding='utf-8',
            delay=True,
            max_total_mb=int(os.environ.get('CPYCMS_LOG_MAX_TOTAL_MB', '256')),
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        listener_handlers.append(file_handler)

    log_queue = queue.Queue(maxsize=int(os.environ.get('CPYCMS_LOG_QUEUE_SIZE', '10000')))
    queue_handler = QueueHandler(log_queue)
    queue_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    root_logger.addHandler(queue_handler)

    _listener = QueueListener(log_queue, *listener_handlers, respect_handler_level=True)
    _listener.start()
    atexit.register(stop_logging_listener)


def stop_logging_listener():
    """进程退出前刷新并停止日志监听线程。"""
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None
