# -*- coding: utf-8 -*-
"""CPYCMS - Django 中间件。"""

import logging
import os
import time


class RequestLogMiddleware:
    """记录每个请求的状态码和耗时，慢请求自动升为 warning。"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('cpycms.request')
        self.slow_ms = int(os.environ.get('CPYCMS_SLOW_REQUEST_MS', '800'))

    def __call__(self, request):
        started = time.perf_counter()
        response = self.get_response(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        log_fn = self.logger.warning if elapsed_ms >= self.slow_ms else self.logger.info
        log_fn(
            'request method=%s path=%s status=%s duration_ms=%.2f ip=%s',
            request.method,
            request.path,
            getattr(response, 'status_code', '-'),
            elapsed_ms,
            request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '-')).split(',')[0].strip(),
        )
        return response
