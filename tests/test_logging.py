# -*- coding: utf-8 -*-
"""CPYCMS 日志系统测试。"""

import gzip
import logging
from io import StringIO
import time

from backend.apps.common.logging import ColorFormatter, CompressedTimedRotatingFileHandler, supports_color


def test_compressed_rotating_handler_gzips_and_cleans_old_logs(tmp_path):
    """日志滚动后应压缩旧日志，并按保留数量清理。"""
    log_file = tmp_path / 'cpycms.log'
    handler = CompressedTimedRotatingFileHandler(
        str(log_file),
        when='S',
        interval=1,
        backupCount=1,
        encoding='utf-8',
        max_total_mb=1,
    )
    logger = logging.getLogger('cpycms-test-rotating')
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info('first log line')
    handler.flush()
    time.sleep(1.1)
    logger.info('second log line')
    handler.flush()
    time.sleep(1.1)
    logger.info('third log line')
    handler.flush()
    handler.close()

    gz_files = sorted(tmp_path.glob('cpycms.log.*.gz'))
    assert len(gz_files) == 1
    with gzip.open(gz_files[0], 'rt', encoding='utf-8') as fh:
        assert 'second log line' in fh.read()


def test_color_formatter_adds_ansi_only_for_console_records():
    """彩色格式器只影响控制台输出，不改变普通 formatter 行为。"""
    record = logging.LogRecord('cpycms-test', logging.ERROR, __file__, 1, 'boom', (), None)
    colored = ColorFormatter('%(levelname)s:%(message)s').format(record)
    plain = logging.Formatter('%(levelname)s:%(message)s').format(record)

    assert '\033[' in colored
    assert colored.endswith('\033[0m')
    assert plain == 'ERROR:boom'


def test_supports_color_respects_no_color(monkeypatch):
    """NO_COLOR 应禁用自动高亮。"""
    stream = StringIO()
    stream.isatty = lambda: True
    monkeypatch.setenv('NO_COLOR', '1')
    monkeypatch.delenv('FORCE_COLOR', raising=False)
    monkeypatch.setenv('CPYCMS_LOG_COLOR', 'auto')

    assert supports_color(stream) is False


def test_supports_color_can_be_forced(monkeypatch):
    """FORCE_COLOR 或 CPYCMS_LOG_COLOR=always 可强制高亮。"""
    stream = StringIO()
    stream.isatty = lambda: False
    monkeypatch.delenv('NO_COLOR', raising=False)
    monkeypatch.setenv('FORCE_COLOR', '1')
    monkeypatch.setenv('CPYCMS_LOG_COLOR', 'auto')

    assert supports_color(stream) is True
