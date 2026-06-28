# -*- coding: utf-8 -*-
"""CPYCMS - 安全搜索辅助。"""

import re

from django.db.models import Q

TOKEN_RE = re.compile(r'[A-Za-z0-9\u4e00-\u9fff]{1,32}', re.UNICODE)


def normalize_search_query(raw_query):
    """将用户搜索词清洗为白名单 token。"""
    text = str(raw_query or '').strip()[:80]
    return TOKEN_RE.findall(text)[:8]


def apply_keyword_filter(queryset, fields, raw_query):
    """给 queryset 添加受控 icontains 查询。"""
    tokens = normalize_search_query(raw_query)
    for token in tokens[:3]:
        clause = Q()
        for field in fields:
            clause |= Q(**{f'{field}__icontains': token})
        queryset = queryset.filter(clause)
    return queryset
