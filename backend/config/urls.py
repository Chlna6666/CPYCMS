# -*- coding: utf-8 -*-
"""CPYCMS - Django URL 配置。"""

from django.conf import settings
from django.urls import include, path, re_path

from backend.apps.common.frontend import frontend_asset, frontend_entry
from backend.apps.common.media import media_file


urlpatterns = [
    path('api/v1/auth/', include('backend.apps.accounts.urls')),
    path('api/v1/', include('backend.apps.cms.urls')),
    re_path(r'^uploads/(?P<path>.+)$', media_file),
    re_path(r'^(?P<path>(assets|bootstrap|vendor)/.*)$', frontend_asset),
    re_path(r'^(?P<path>favicon\.svg|favicon\.ico|manifest\.webmanifest|robots\.txt)$', frontend_asset),
    re_path(r'^(?!api/|uploads/|static/)(?P<path>.*)$', frontend_entry),
]
