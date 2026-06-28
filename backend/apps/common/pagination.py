# -*- coding: utf-8 -*-
"""CPYCMS - DRF 风格分页辅助。"""

from math import ceil


def page_number(request, default=1):
    """读取页码。"""
    try:
        return max(1, int(request.query_params.get('page', default)))
    except (TypeError, ValueError):
        return default


def paginate_queryset(queryset, request, page_size):
    """返回 DRF 风格分页结果。"""
    page = page_number(request)
    page_size = max(1, min(int(page_size), 100))
    count = queryset.count()
    start = (page - 1) * page_size
    items = list(queryset[start:start + page_size])
    total_pages = max(1, ceil(count / page_size)) if count else 1
    return {
        'count': count,
        'next': page + 1 if page < total_pages else None,
        'previous': page - 1 if page > 1 else None,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'results': items,
    }
