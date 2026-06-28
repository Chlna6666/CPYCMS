# -*- coding: utf-8 -*-
"""CPYCMS - 上传与路径安全工具。"""

from pathlib import Path
import os
import re
import uuid

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile


SAFE_NAME_RE = re.compile(r'[^A-Za-z0-9_.\-\u4e00-\u9fff]+')


def clean_str(value, max_len=None):
    """清理字符串。"""
    text = str(value or '').strip()
    return text[:max_len] if max_len else text


def secure_filename_chinese(filename):
    """保留中英文和常见安全符号，避免路径片段。"""
    name = os.path.basename(str(filename or '')).strip()
    name = SAFE_NAME_RE.sub('_', name)
    if not name or name in {'.', '..'}:
        name = f'upload-{uuid.uuid4().hex}'
    return name[:180]


def safe_join_under(base_dir, *parts):
    """拼接路径并确保仍位于 base_dir 内。"""
    base_path = Path(base_dir).resolve()
    target = (base_path.joinpath(*parts)).resolve()
    if os.path.commonpath([str(base_path), str(target)]) != str(base_path):
        raise ValueError('非法文件路径')
    return target


def is_path_under(base_dir, target_path):
    """判断路径是否位于指定目录下。"""
    try:
        safe_join_under(base_dir, os.path.relpath(target_path, base_dir))
        return True
    except ValueError:
        return False


def validate_upload(file_obj: UploadedFile, allowed_ext):
    """校验上传文件扩展名和大小。"""
    if not file_obj:
        return False, '请选择文件'
    name = file_obj.name or ''
    if '/' in name or '\\' in name or '..' in name:
        return False, '文件名包含非法路径片段'
    if '.' not in name:
        return False, '文件无扩展名'
    ext = name.rsplit('.', 1)[1].lower()
    if ext not in allowed_ext:
        return False, f'不允许的文件格式: {ext}'
    if file_obj.size <= 0:
        return False, '文件为空'
    if file_obj.size > settings.MAX_UPLOAD_SIZE:
        return False, f'文件过大(最大{settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB)'
    return True, ''


def save_upload(file_obj: UploadedFile, subdir):
    """保存上传文件并返回绝对路径和 URL。"""
    safe_name = secure_filename_chinese(file_obj.name)
    target_dir = Path(settings.MEDIA_ROOT) / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = safe_join_under(target_dir, safe_name)
    with target_path.open('wb') as output:
        for chunk in file_obj.chunks():
            output.write(chunk)
    return str(target_path), f'{settings.MEDIA_URL}{subdir}/{safe_name}'
