# -*- coding: utf-8 -*-
"""CPYCMS pytest-django 公共夹具。"""

import json

import pytest


def json_request(client, method, path, payload=None, **extra):
    """发送 JSON 请求并返回响应。"""
    data = json.dumps(payload or {}, ensure_ascii=False)
    return getattr(client, method)(path, data=data, content_type='application/json', **extra)


@pytest.fixture()
def initialized_client(client, db):
    """完成初始化并登录管理员的 Django 测试客户端。"""
    response = json_request(client, 'post', '/api/v1/init/setup/', {
        'username': 'admin',
        'password': 'secret123',
        'site_name': 'CPYCMS Test',
        'site_slogan': '测试站点',
        'author_email': 'admin@example.com',
    })
    assert response.status_code == 200

    login = json_request(client, 'post', '/api/v1/auth/login/', {
        'username': 'admin',
        'password': 'secret123',
    })
    assert login.status_code == 200
    return client
