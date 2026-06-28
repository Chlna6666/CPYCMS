# -*- coding: utf-8 -*-
"""CPYCMS - Gunicorn 使用的 Django WSGI 入口。"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

application = get_wsgi_application()

from backend.apps.common.site_runtime import refresh_site_runtime_cache  # noqa: E402

refresh_site_runtime_cache()
