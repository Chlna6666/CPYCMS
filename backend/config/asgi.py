# -*- coding: utf-8 -*-
"""CPYCMS - Django ASGI 入口。"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

application = get_asgi_application()

from backend.apps.common.site_runtime import refresh_site_runtime_cache  # noqa: E402

refresh_site_runtime_cache()
