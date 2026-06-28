# -*- coding: utf-8 -*-
"""CPYCMS Django API 冒烟与安全测试。"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.test import override_settings
from django.test import Client
import json
import pytest

from backend.apps.cms.models import Article, ArticleComment, Message, Resource, Tag
from backend.apps.common import authentication, database
from backend.apps.common.uploads import validate_upload


pytestmark = pytest.mark.django_db


def json_request(client, method, path, payload=None, **extra):
    """发送 JSON 请求并返回响应。"""
    data = json.dumps(payload or {}, ensure_ascii=False)
    return getattr(client, method)(path, data=data, content_type='application/json', **extra)


def test_init_login_and_auth_guard(client):
    """初始化、登录、退出和后台鉴权应可正常工作。"""
    assert client.get('/api/v1/init/check/').json()['initialized'] is False

    bootstrap_state = client.get('/api/v1/site/bootstrap/').json()
    assert bootstrap_state['initialized'] is False
    assert bootstrap_state['categories'] == []

    assert client.get('/api/v1/admin/articles/').status_code == 401

    init = json_request(client, 'post', '/api/v1/init/setup/', {
        'username': 'admin',
        'password': 'secret123',
        'bound_domains': 'https://cms.example.com',
    })
    assert init.status_code == 200
    assert '成功' in init.json()['detail']
    assert init.json()['initialized'] is True
    assert client.get('/api/v1/init/check/').json()['initialized'] is True

    bootstrap = client.get('/api/v1/site/bootstrap/').json()
    assert bootstrap['info']['site_name'] == '我的CMS站点'
    assert bootstrap['info']['bound_domains'] == 'https://cms.example.com'
    assert len(bootstrap['categories']) >= 4
    assert len(bootstrap['tags']) >= 5
    hello = Article.objects.get(slug='hello-cpycms')
    assert hello.title == 'Hello CPYCMS'
    assert hello.status == 'published'
    assert '```mermaid' in hello.content

    duplicate = json_request(client, 'post', '/api/v1/init/setup/', {'username': 'admin2', 'password': 'secret123'})
    assert duplicate.status_code == 400

    bad_login = json_request(client, 'post', '/api/v1/auth/login/', {'username': 'admin', 'password': 'bad-pass'})
    assert bad_login.status_code == 401

    login = json_request(client, 'post', '/api/v1/auth/login/', {'username': 'admin', 'password': 'secret123'})
    assert login.status_code == 200
    assert login.json()['username'] == 'admin'

    assert client.get('/api/v1/auth/session/').json()['logged_in'] is True
    assert client.get('/api/v1/admin/articles/').status_code == 200
    assert json_request(client, 'post', '/api/v1/auth/logout/').status_code == 200
    assert client.get('/api/v1/admin/articles/').status_code == 401


def test_non_admin_user_cannot_access_admin_api(client):
    """普通登录用户不能进入 CPYCMS 管理后台接口。"""
    User = get_user_model()
    User.objects.create_user(username='visitor', password='secret123', is_staff=False, is_superuser=False)

    login = json_request(client, 'post', '/api/v1/auth/login/', {
        'username': 'visitor',
        'password': 'secret123',
    })
    assert login.status_code == 403
    assert '后台管理权限' in login.json()['detail']

    user = User.objects.get(username='visitor')
    client.force_login(user)
    blocked = client.get('/api/v1/admin/categories/')
    assert blocked.status_code == 401
    assert '未登录' in blocked.json()['detail']


def test_forged_session_without_binding_is_not_admin(client):
    """伪造或旧版无绑定 sessionid 不能冒充管理员登录态。"""
    User = get_user_model()
    admin = User.objects.create_superuser(username='admin', password='secret123')
    forged = SessionStore()
    forged['_auth_user_id'] = str(admin.pk)
    forged['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
    forged['_auth_user_hash'] = admin.get_session_auth_hash()
    forged.save()

    attacker = Client()
    attacker.cookies[settings.SESSION_COOKIE_NAME] = forged.session_key

    blocked = attacker.get('/api/v1/admin/categories/')

    assert blocked.status_code == 401


@override_settings(
    ALLOWED_HOSTS=['127.0.0.1', 'testserver'],
    USE_X_FORWARDED_HOST=False,
    CSRF_TRUSTED_ORIGINS=[],
)
def test_login_is_not_blocked_by_proxy_origin_mismatch(client):
    """登录接口不应因反代内部 Host 与公网 Origin 不一致被全局 CSRF 误杀。"""
    secure_client = Client(enforce_csrf_checks=True)
    assert json_request(secure_client, 'post', '/api/v1/init/setup/', {
        'username': 'admin',
        'password': 'secret123',
    }, HTTP_HOST='127.0.0.1:5000').status_code == 200

    login = secure_client.post('/api/v1/auth/login/', data=json.dumps({
        'username': 'admin',
        'password': 'secret123',
    }), content_type='application/json', HTTP_HOST='127.0.0.1:5000', HTTP_ORIGIN='https://cms.chlna6666.com', HTTP_REFERER='https://cms.chlna6666.com/admin/login')

    assert login.status_code == 200
    assert login.json()['username'] == 'admin'


def test_bound_domain_allows_csrf_origin_after_login(client):
    """初始化绑定域名后，已登录后台写接口应信任该 Origin。"""
    secure_client = Client(enforce_csrf_checks=True)
    assert json_request(secure_client, 'post', '/api/v1/init/setup/', {
        'username': 'admin',
        'password': 'secret123',
        'bound_domains': 'https://cms.example.com',
    }).status_code == 200
    secure_client.get('/api/v1/auth/csrf/')
    token = secure_client.cookies[settings.CSRF_COOKIE_NAME].value
    assert secure_client.post('/api/v1/auth/login/', data=json.dumps({
        'username': 'admin',
        'password': 'secret123',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token).status_code == 200

    token = secure_client.cookies[settings.CSRF_COOKIE_NAME].value
    allowed = secure_client.post('/api/v1/admin/categories/', data=json.dumps({
        'name': '绑定域名分类',
        'slug': 'bound-domain-category',
    }), content_type='application/json', HTTP_ORIGIN='https://cms.example.com', HTTP_X_CSRFTOKEN=token)
    assert allowed.status_code == 200

    blocked = secure_client.post('/api/v1/admin/categories/', data=json.dumps({
        'name': '非法域名分类',
        'slug': 'blocked-domain-category',
    }), content_type='application/json', HTTP_ORIGIN='https://evil.example.com', HTTP_X_CSRFTOKEN=token)
    assert blocked.status_code == 403


@override_settings(
    ALLOWED_HOSTS=['cms.chlna6666.com', '127.0.0.1', 'testserver'],
    USE_X_FORWARDED_HOST=True,
    SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'),
    CSRF_TRUSTED_ORIGINS=[],
)
def test_https_same_origin_proxy_allows_public_and_admin_writes(client):
    """HTTPS 反代同域 Origin 应允许公开写接口和后台写接口。"""
    secure_client = Client(enforce_csrf_checks=True)
    host_headers = {
        'HTTP_HOST': '127.0.0.1:5000',
        'HTTP_X_FORWARDED_HOST': 'cms.chlna6666.com',
        'HTTP_X_FORWARDED_PROTO': 'https',
        'HTTP_ORIGIN': 'https://cms.chlna6666.com',
    }

    assert json_request(secure_client, 'post', '/api/v1/init/setup/', {
        'username': 'admin',
        'password': 'secret123',
    }, **host_headers).status_code == 200

    secure_client.get('/api/v1/auth/csrf/', **host_headers)
    token = secure_client.cookies[settings.CSRF_COOKIE_NAME].value
    assert secure_client.post('/api/v1/auth/login/', data=json.dumps({
        'username': 'admin',
        'password': 'secret123',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token, **host_headers).status_code == 200

    token = secure_client.cookies[settings.CSRF_COOKIE_NAME].value
    message = secure_client.post('/api/v1/messages/create/', data=json.dumps({
        'nickname': '访客',
        'content': 'HTTPS 同域留言',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token, **host_headers)
    assert message.status_code == 200

    settings_response = secure_client.put('/api/v1/admin/settings/', data=json.dumps({
        'site_name': 'HTTPS Same Origin',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token, **host_headers)
    assert settings_response.status_code == 200

    blocked = secure_client.put('/api/v1/admin/settings/', data=json.dumps({
        'site_name': 'Blocked Origin',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token, HTTP_HOST='127.0.0.1:5000', HTTP_X_FORWARDED_HOST='cms.chlna6666.com', HTTP_X_FORWARDED_PROTO='https', HTTP_ORIGIN='https://evil.example.com')
    assert blocked.status_code == 403

    logout = secure_client.post('/api/v1/auth/logout/', data='{}', content_type='application/json', HTTP_X_CSRFTOKEN=token, **host_headers)
    assert logout.status_code == 200


@override_settings(
    ALLOWED_HOSTS=['127.0.0.1', 'testserver'],
    USE_X_FORWARDED_HOST=False,
    CSRF_TRUSTED_ORIGINS=[],
)
def test_logged_in_comment_allows_browser_same_origin_when_proxy_host_is_internal(client):
    """反代未传真实 Host 时，浏览器同源评论请求不应被 CSRF 误杀。"""
    secure_client = Client(enforce_csrf_checks=True)
    internal_host = {'HTTP_HOST': '127.0.0.1:5000'}
    browser_same_origin = {
        **internal_host,
        'HTTP_ORIGIN': 'https://cms.chlna6666.com',
        'HTTP_REFERER': 'https://cms.chlna6666.com/article/hello-cpycms',
        'HTTP_SEC_FETCH_SITE': 'same-origin',
    }

    assert json_request(secure_client, 'post', '/api/v1/init/setup/', {
        'username': 'admin',
        'password': 'secret123',
    }, **internal_host).status_code == 200
    secure_client.get('/api/v1/auth/csrf/', **internal_host)
    token = secure_client.cookies[settings.CSRF_COOKIE_NAME].value
    login = secure_client.post('/api/v1/auth/login/', data=json.dumps({
        'username': 'admin',
        'password': 'secret123',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token, **internal_host)
    assert login.status_code == 200
    token = secure_client.cookies[settings.CSRF_COOKIE_NAME].value

    allowed = secure_client.post('/api/v1/articles/hello-cpycms/comments/create/', data=json.dumps({
        'content': '管理员前台直接评论',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token, **browser_same_origin)
    assert allowed.status_code == 200
    assert '评论已发布' in allowed.json()['detail']

    blocked = secure_client.post('/api/v1/articles/hello-cpycms/comments/create/', data=json.dumps({
        'content': '跨站评论应该被拦截',
    }), content_type='application/json', HTTP_X_CSRFTOKEN=token, HTTP_HOST='127.0.0.1:5000', HTTP_ORIGIN='https://evil.example.com', HTTP_REFERER='https://evil.example.com/article/hello-cpycms', HTTP_SEC_FETCH_SITE='cross-site')
    assert blocked.status_code == 403


def test_init_setup_works_when_session_table_is_missing(client, monkeypatch):
    """浏览器带旧 sessionid 且 session 表不可用时，初始化接口不应被认证层阻断。"""

    monkeypatch.setattr(authentication, 'table_exists', lambda table_name: False)
    client.cookies['sessionid'] = 'stale-session-id'
    check = client.get('/api/v1/init/check/')
    assert check.json()['initialized'] is False
    assert check.cookies['sessionid'].value == ''
    assert check.cookies['sessionid']['max-age'] == 0

    response = json_request(client, 'post', '/api/v1/init/setup/', {
        'username': 'freshadmin',
        'password': 'secret123',
    })

    assert response.status_code == 200
    assert response.json()['initialized'] is True


def test_article_and_category_crud(initialized_client):
    """分类、标签和文章基础增删改查应保持可用。"""
    client = initialized_client

    tag = json_request(client, 'post', '/api/v1/admin/tags/', {
        'name': '课程标签',
        'color': '#2563eb',
    }).json()
    assert tag['name'] == '课程标签'

    updated_tag = json_request(client, 'put', f"/api/v1/admin/tags/{tag['id']}/", {
        'name': '课程标签更新',
        'color': '#16a34a',
    }).json()
    assert updated_tag['name'] == '课程标签更新'
    assert updated_tag['color'] == '#16a34a'

    duplicate_tag = json_request(client, 'post', '/api/v1/admin/tags/', {
        'name': '课程标签更新',
    })
    assert duplicate_tag.status_code == 400

    category = json_request(client, 'post', '/api/v1/admin/categories/', {
        'name': '课程记录',
        'slug': 'course-notes',
        'description': '课程作业记录',
        'sort_order': 9,
    }).json()
    assert category['name'] == '课程记录'

    article = json_request(client, 'post', '/api/v1/admin/articles/create/', {
        'title': 'Django 与 Vue 联调笔记',
        'slug': 'django-vue-notes',
        'content': '# 联调\n\n```python\nprint("CPYCMS")\n```',
        'summary': '接口联调记录',
        'category_id': category['id'],
        'status': 'published',
    }).json()
    assert article['status'] == 'published'

    detail = client.get(f"/api/v1/admin/articles/{article['id']}/").json()
    assert detail['slug'] == 'django-vue-notes'

    updated = json_request(client, 'put', f"/api/v1/admin/articles/{article['id']}/", {
        'title': 'Django 与 Vue3 联调笔记',
        'status': 'draft',
    }).json()
    assert updated['title'] == 'Django 与 Vue3 联调笔记'
    assert updated['status'] == 'draft'

    assert client.delete(f"/api/v1/admin/articles/{article['id']}/").status_code == 200
    assert client.delete(f"/api/v1/admin/categories/{category['id']}/").status_code == 200
    assert client.delete(f"/api/v1/admin/tags/{tag['id']}/").status_code == 200
    assert not Tag.objects.filter(id=tag['id']).exists()


def test_article_and_work_like_deduplicates_by_fingerprint(initialized_client):
    """文章和作品点赞应按浏览器指纹去重，避免重复刷赞。"""
    client = initialized_client
    article = json_request(client, 'post', '/api/v1/admin/articles/create/', {
        'title': '点赞测试文章',
        'slug': 'like-enabled-article',
        'content': '文章正文',
        'status': 'published',
    }).json()
    work = json_request(client, 'post', '/api/v1/admin/works/', {
        'title': '点赞测试作品',
        'description': '作品说明',
        'content': '作品详情',
        'status': 'published',
    }).json()

    article_like = json_request(client, 'post', f"/api/v1/articles/{article['slug']}/like/", {
        'client_fingerprint': 'c' * 64,
    })
    assert article_like.status_code == 200
    assert article_like.json()['like_count'] == 1
    assert json_request(client, 'post', f"/api/v1/articles/{article['slug']}/like/", {
        'client_fingerprint': 'c' * 64,
    }).status_code == 400
    assert client.get(f"/api/v1/articles/{article['slug']}/").json()['like_count'] == 1

    work_like = json_request(client, 'post', f"/api/v1/works/{work['id']}/like/", {
        'client_fingerprint': 'd' * 64,
    })
    assert work_like.status_code == 200
    assert work_like.json()['like_count'] == 1
    assert json_request(client, 'post', f"/api/v1/works/{work['id']}/like/", {
        'client_fingerprint': 'd' * 64,
    }).status_code == 400
    assert client.get(f"/api/v1/works/{work['id']}/").json()['like_count'] == 1


def test_article_comments_require_email_and_admin_approval(initialized_client):
    """文章评论应要求邮箱、记录客户端信息，并经后台审核后才公开展示。"""
    client = initialized_client
    public_client = Client()
    article = json_request(client, 'post', '/api/v1/admin/articles/create/', {
        'title': '支持评论的文章',
        'slug': 'comment-enabled-article',
        'content': '文章正文',
        'status': 'published',
    }).json()

    missing_email = json_request(client, 'post', f"/api/v1/articles/{article['slug']}/comments/create/", {
        'nickname': '访客',
        'content': '缺少邮箱的评论',
    })
    assert missing_email.status_code == 200
    assert '评论已发布' in missing_email.json()['detail']

    admin_direct = ArticleComment.objects.get(id=missing_email.json()['id'])
    assert admin_direct.is_approved is True
    assert admin_direct.email == ''
    assert admin_direct.nickname == 'admin'
    assert admin_direct.author_role == 'admin'

    impersonation = json_request(public_client, 'post', f"/api/v1/articles/{article['slug']}/comments/create/", {
        'nickname': '站长',
        'email': 'fake@example.com',
        'content': '冒充管理员的评论',
        'client_fingerprint': 'f' * 64,
    })
    assert impersonation.status_code == 400
    assert '访客昵称' in impersonation.json()['detail']

    missing_email_public = json_request(public_client, 'post', f"/api/v1/articles/{article['slug']}/comments/create/", {
        'nickname': '访客',
        'content': '缺少邮箱的评论',
    })
    assert missing_email_public.status_code == 400

    submit = json_request(
        public_client,
        'post',
        f"/api/v1/articles/{article['slug']}/comments/create/",
        {
            'nickname': '访客',
            'email': 'guest@example.com',
            'content': '<script>alert(1)</script>课程作业做得不错',
            'client_fingerprint': 'a' * 64,
        },
        HTTP_USER_AGENT='Mozilla/5.0 Windows NT Chrome/120.0',
    )
    assert submit.status_code == 200
    assert '等待审核' in submit.json()['detail']

    public_initial = public_client.get(f"/api/v1/articles/{article['slug']}/comments/").json()
    assert public_initial['count'] == 1
    assert public_initial['results'][0]['email_masked'] == ''
    assert public_initial['results'][0]['author_role'] == 'admin'
    assert public_initial['results'][0]['is_admin_author'] is True
    assert client.get(f"/api/v1/articles/{article['slug']}/comments/").json()['count'] == 2

    admin_items = client.get('/api/v1/admin/comments/').json()['results']
    assert len(admin_items) == 2
    comment = next(item for item in admin_items if item['email'] == 'guest@example.com')
    assert comment['email'] == 'guest@example.com'
    assert comment['browser'] == 'Chrome'
    assert comment['os_name'] == 'Windows'
    assert len(comment['fingerprint_hash']) == 12
    assert '<script>' not in comment['content']

    reply = json_request(client, 'put', f"/api/v1/admin/comments/{comment['id']}/reply/", {
        'reply': '感谢反馈，已收到你的建议。',
    })
    assert reply.status_code == 200

    replied_admin = client.get('/api/v1/admin/comments/').json()['results'][0]
    assert replied_admin['is_approved'] is True
    assert replied_admin['is_replied'] is True
    assert replied_admin['reply'] == '感谢反馈，已收到你的建议。'

    assert json_request(client, 'put', f"/api/v1/admin/comments/{comment['id']}/approve/").status_code == 200
    public_after = public_client.get(f"/api/v1/articles/{article['slug']}/comments/").json()['results']
    assert len(public_after) == 2
    guest_public = next(item for item in public_after if item['email_masked'].startswith('gu'))
    assert guest_public['reply'] == '感谢反馈，已收到你的建议。'
    assert guest_public['author_role'] == 'visitor'
    assert guest_public['is_admin_author'] is False
    for item in public_after:
        assert 'ip_address' not in item
        assert 'email' not in item
        assert 'fingerprint_hash' not in item


def test_article_comment_reply_requires_admin(initialized_client):
    """未登录用户不能调用文章评论回复接口。"""
    admin_client = initialized_client
    guest_client = Client()
    article = json_request(admin_client, 'post', '/api/v1/admin/articles/create/', {
        'title': '评论回复权限测试',
        'slug': 'comment-reply-auth',
        'content': '文章正文',
        'status': 'published',
    }).json()
    submit = json_request(admin_client, 'post', f"/api/v1/articles/{article['slug']}/comments/create/", {
        'nickname': '访客',
        'email': 'guest@example.com',
        'content': '待回复评论',
    })
    comment_id = submit.json()['id']

    response = json_request(guest_client, 'put', f'/api/v1/admin/comments/{comment_id}/reply/', {'reply': '未授权回复'})

    assert response.status_code == 401


def test_article_comment_rate_limit(initialized_client):
    """同一客户端短时间频繁提交评论应被限频。"""
    admin_client = initialized_client
    public_client = Client()
    article = json_request(admin_client, 'post', '/api/v1/admin/articles/create/', {
        'title': '评论限频测试',
        'slug': 'comment-rate-limit',
        'content': '文章正文',
        'status': 'published',
    }).json()

    for idx in range(3):
        response = json_request(public_client, 'post', f"/api/v1/articles/{article['slug']}/comments/create/", {
            'nickname': f'访客{idx}',
            'email': f'guest{idx}@example.com',
            'content': f'第 {idx} 条评论',
            'client_fingerprint': 'b' * 64,
        })
        assert response.status_code == 200

    blocked = json_request(public_client, 'post', f"/api/v1/articles/{article['slug']}/comments/create/", {
        'nickname': '访客4',
        'email': 'guest4@example.com',
        'content': '第四条评论',
        'client_fingerprint': 'b' * 64,
    })
    assert blocked.status_code == 429


def test_work_message_settings_and_stats(initialized_client):
    """作品、留言、设置和统计面板应具备基础业务闭环。"""
    client = initialized_client

    work = json_request(client, 'post', '/api/v1/admin/works/', {
        'title': 'CPYCMS 课程作业',
        'description': 'Vue3 + Django 全栈系统',
        'content': '作品说明',
        'tech_stack': ['Django', 'Vue3', 'SQLite'],
        'status': 'published',
    }).json()

    assert client.get(f"/api/v1/works/{work['id']}/").json()['title'] == 'CPYCMS 课程作业'
    assert json_request(client, 'post', f"/api/v1/works/{work['id']}/like/", {
        'client_fingerprint': 'e' * 64,
    }).json()['like_count'] == 1

    message = json_request(client, 'post', '/api/v1/messages/create/', {
        'nickname': '访客',
        'email': 'guest@example.com',
        'content': '课程项目功能完整。',
    })
    assert '留言已发布' in message.json()['detail']

    pending = client.get('/api/v1/admin/messages/').json()['results']
    assert len(pending) == 1
    assert pending[0]['author_role'] == 'admin'
    assert pending[0]['is_admin_author'] is True
    assert json_request(client, 'put', f"/api/v1/admin/messages/{pending[0]['id']}/reply/", {'reply': '感谢反馈'}).status_code == 200

    public_message_client = Client()
    impersonation_message = json_request(public_message_client, 'post', '/api/v1/messages/create/', {
        'nickname': '管理员',
        'content': '冒充管理员留言',
    })
    assert impersonation_message.status_code == 400

    public_message = json_request(public_message_client, 'post', '/api/v1/messages/create/', {
        'nickname': '访客',
        'email': 'public@example.com',
        'content': '公开留言等待审核。',
    })
    assert '等待审核' in public_message.json()['detail']
    public_record = Message.objects.get(content='公开留言等待审核。')
    public_record.is_approved = True
    public_record.save(update_fields=['is_approved'])
    public_messages = public_message_client.get('/api/v1/messages/').json()['results']
    public_item = next(item for item in public_messages if item['content'] == '公开留言等待审核。')
    assert public_item['author_role'] == 'visitor'
    assert public_item['is_admin_author'] is False
    assert 'email' not in public_item
    assert 'ip_address' not in public_item

    assert json_request(client, 'put', '/api/v1/admin/settings/', {
        'site_name': 'CPYCMS 测试站点',
        'footer_height': 'large',
        'footer_note': '课程作业展示站点',
        'icp_beian_number': '粤ICP备12345678号-1',
        'police_beian_number': '粤公网安备 44200102445782号',
        'friend_links': '[{"name":"Vue","url":"https://vuejs.org"}]',
        'hero_slides': '[{"title":"第一屏","subtitle":"课程项目","ctaText":"看文章","ctaLink":"/articles"}]',
        'theme_primary_color': '#0f766e',
        'theme_accent_color': '#f97316',
    }).status_code == 200
    site_settings = client.get('/api/v1/admin/settings/').json()
    assert site_settings['site_name'] == 'CPYCMS 测试站点'
    assert site_settings['footer_height'] == 'large'
    assert 'vuejs.org' in site_settings['friend_links']

    assert json_request(client, 'put', '/api/v1/admin/settings/', {'theme_primary_color': 'blue'}).status_code == 400
    assert json_request(client, 'put', '/api/v1/admin/settings/', {'footer_height': 'giant'}).status_code == 400
    assert json_request(client, 'put', '/api/v1/admin/settings/', {'friend_links': '[{"name":"Local","url":"javascript:alert(1)"}]'}).status_code == 400
    assert json_request(client, 'put', '/api/v1/admin/settings/', {'hero_slides': '[{"title":"外链","ctaLink":"https://example.com"}]'}).status_code == 400
    assert json_request(client, 'put', '/api/v1/admin/settings/', {'site_logo': 'https://example.com/logo.png'}).status_code == 400
    assert json_request(client, 'put', '/api/v1/admin/settings/', {'icp_beian_number': '<script>alert(1)</script>'}).status_code == 400

    stats = client.get('/api/v1/admin/stats/').json()
    assert stats['work_count'] == 1
    assert stats['message_count'] == 2


def test_resource_upload_download_delete(initialized_client):
    """资源文件上传、下载和物理删除应只操作上传目录内文件。"""
    client = initialized_client
    upload_file = SimpleUploadedFile('course.md', b'# CPYCMS resource', content_type='text/markdown')
    response = client.post('/api/v1/admin/resources/', {
        'title': '课程资料',
        'description': 'Markdown 资料',
        'file': upload_file,
    })
    assert response.status_code == 200
    upload = response.json()

    resource = Resource.objects.get(id=upload['id'])
    saved_path = resource.file_path

    download = client.get(f"/api/v1/resources/{upload['id']}/download/")
    assert download.status_code == 200
    assert b'CPYCMS resource' in b''.join(download.streaming_content)

    assert client.delete(f"/api/v1/admin/resources/{upload['id']}/").status_code == 200
    assert not Resource.objects.filter(id=upload['id']).exists()

    from pathlib import Path
    assert not Path(saved_path).exists()
    assert str(settings.MEDIA_ROOT) in saved_path


@override_settings(DEBUG=False)
def test_uploaded_media_file_is_served_in_production_mode(client, settings, tmp_path):
    """生产模式下也应能读取本地 uploads 文件，路径穿越必须被拒绝。"""
    settings.MEDIA_ROOT = tmp_path
    target_dir = tmp_path / 'works'
    target_dir.mkdir(parents=True)
    image_path = target_dir / 'cover.png'
    image_path.write_bytes(b'\x89PNG\r\n\x1a\n')
    resource_dir = tmp_path / 'resources'
    resource_dir.mkdir()
    (resource_dir / 'secret.pdf').write_bytes(b'%PDF private')
    (target_dir / 'note.txt').write_text('not public image', encoding='utf-8')

    response = client.get('/uploads/works/cover.png')

    assert response.status_code == 200
    assert b''.join(response.streaming_content).startswith(b'\x89PNG')
    assert client.get('/uploads/../cpycms.db').status_code == 404
    assert client.get('/uploads/works/../resources/secret.pdf').status_code == 404
    assert client.get('/uploads/resources/secret.pdf').status_code == 404
    assert client.get('/uploads/works/note.txt').status_code == 404


def test_upload_security_rejects_path_traversal_and_svg(initialized_client):
    """上传接口应拒绝路径穿越文件名、空文件和 SVG 图片。"""
    client = initialized_client

    class FakeUpload:
        name = '../bad.md'
        size = 1

    fake_bad = FakeUpload()
    ok, _message = validate_upload(fake_bad, {'md'})
    assert ok is False

    svg = client.post('/api/v1/admin/upload/image/', {
        'image': SimpleUploadedFile('logo.svg', b'<svg><script>alert(1)</script></svg>', content_type='image/svg+xml'),
    })
    assert svg.status_code == 400

    empty = client.post('/api/v1/admin/resources/', {
        'title': 'empty',
        'file': SimpleUploadedFile('empty.md', b'', content_type='text/markdown'),
    })
    assert empty.status_code == 400


def test_admin_message_delete_removes_record(initialized_client):
    """留言删除接口应删除数据库记录。"""
    client = initialized_client
    assert json_request(client, 'post', '/api/v1/messages/create/', {'nickname': 'A', 'content': '待删除留言'}).status_code == 200
    msg_id = client.get('/api/v1/admin/messages/').json()['results'][0]['id']
    assert client.delete(f'/api/v1/admin/messages/{msg_id}/').status_code == 200
    assert Message.objects.filter(id=msg_id).exists() is False


def test_init_returns_conflict_when_database_switch_is_unavailable(client, monkeypatch):
    """无法切换物理数据库时初始化应返回 409，而不是抛出 500。"""

    def fake_backup():
        raise RuntimeError('SQLite 数据库文件被占用，请关闭旧后端进程或数据库查看器后重试迁移')

    monkeypatch.setattr(database, 'backup_legacy_database', fake_backup)
    response = json_request(client, 'post', '/api/v1/init/setup/', {
        'username': 'fallback',
        'password': 'secret123',
    })
    assert response.status_code == 409
    assert response.json()['detail']
