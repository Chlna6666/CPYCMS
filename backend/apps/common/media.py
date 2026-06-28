# -*- coding: utf-8 -*-
"""CPYCMS - 本地上传文件读取视图。"""

import logging
from mimetypes import guess_type
from pathlib import PurePosixPath

from django.conf import settings
from django.http import FileResponse, Http404

from backend.apps.common.uploads import safe_join_under


PUBLIC_IMAGE_DIRS = {'articles', 'works', 'site'}
PUBLIC_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
logger = logging.getLogger('cpycms.media')


def normalize_public_media_path(path: str):
    """校验并拆分公开媒体路径。

    只允许公开图片目录，资源文件必须走带发布状态校验的下载接口。
    """
    raw = str(path or '').strip()
    if not raw or raw.startswith('/') or '\\' in raw:
        raise Http404('文件路径无效')
    parts = PurePosixPath(raw).parts
    if len(parts) < 2 or any(part in {'', '.', '..'} for part in parts):
        raise Http404('文件路径无效')
    if parts[0] not in PUBLIC_IMAGE_DIRS:
        raise Http404('文件路径无效')
    if PurePosixPath(parts[-1]).suffix.lower() not in PUBLIC_IMAGE_EXTENSIONS:
        raise Http404('文件类型不允许公开访问')
    return parts


def media_file(_request, path: str):
    """读取 MEDIA_ROOT 内的本地上传文件，拒绝路径穿越。"""
    try:
        parts = normalize_public_media_path(path)
        file_path = safe_join_under(settings.MEDIA_ROOT, *parts)
    except (Http404, ValueError) as exc:
        logger.warning('media rejected path=%s media_root=%s reason=%s', path, settings.MEDIA_ROOT, exc)
        raise Http404('文件路径无效') from exc
    if not file_path.is_file():
        logger.warning('media missing path=%s resolved=%s media_root=%s', path, file_path, settings.MEDIA_ROOT)
        raise Http404('文件不存在')
    content_type, _encoding = guess_type(str(file_path))
    response = FileResponse(file_path.open('rb'), content_type=content_type or 'application/octet-stream')
    response['X-Content-Type-Options'] = 'nosniff'
    return response
