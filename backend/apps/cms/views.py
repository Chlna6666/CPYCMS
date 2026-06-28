# -*- coding: utf-8 -*-
"""CPYCMS - CMS REST API。"""

from datetime import timedelta
from pathlib import Path
import json
import os
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from slugify import slugify

from backend.apps.cms.models import Article, ArticleComment, Category, ContentLike, Message, Resource, SiteSetting, Tag, Work
from backend.apps.cms.serializers import (
    admin_comment_dict,
    article_dict,
    category_dict,
    message_dict,
    public_comment_dict,
    resource_dict,
    tag_dict,
    work_dict,
)
from backend.apps.common.comment_security import detect_client_info, hash_client_fingerprint, normalize_plain_text, validate_comment_payload
from backend.apps.common.database import django_schema_ready, ensure_database_schema
from backend.apps.common.pagination import paginate_queryset
from backend.apps.common.permissions import admin_required
from backend.apps.common.search import apply_keyword_filter, normalize_search_query
from backend.apps.common.settings_defaults import DEFAULT_SITE_SETTINGS
from backend.apps.common.site_runtime import get_site_settings_cached, parse_bound_origins, refresh_site_runtime_cache
from backend.apps.common.uploads import clean_str, is_path_under, save_upload, validate_upload

ARTICLE_STATUS = {'draft', 'published', 'archived'}
PUBLIC_STATUS = {'draft', 'published'}
LIKE_TARGETS = {'article', 'work'}
RESERVED_AUTHOR_NAMES = {'admin', 'administrator', 'webmaster', 'cpycms', '管理员', '站长', '站点管理员', '官方', '博主', '作者'}


def get_client_ip(request):
    """获取客户端 IP。"""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')


def is_initialized():
    """判断系统是否已初始化。"""
    if not django_schema_ready():
        return False
    return get_user_model().objects.filter(is_active=True).filter(Q(is_superuser=True) | Q(is_staff=True)).exists()


def init_state_response(initialized=None, status=200, **payload):
    """返回不缓存的初始化状态响应，避免浏览器或代理复用旧状态。"""
    data = {'initialized': is_initialized() if initialized is None else bool(initialized)}
    data.update(payload)
    response = Response(data, status=status)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    if not data['initialized']:
        response.delete_cookie(settings.SESSION_COOKIE_NAME, path='/', samesite=settings.SESSION_COOKIE_SAMESITE)
        response.delete_cookie(settings.CSRF_COOKIE_NAME, path='/', samesite=settings.CSRF_COOKIE_SAMESITE)
    return response


def is_admin_user(request):
    """判断当前请求是否来自后台管理员。"""
    user = getattr(request, 'user', None)
    return bool(user and user.is_authenticated and user.is_active and (user.is_staff or user.is_superuser))


def uses_reserved_author_name(nickname):
    """访客昵称不能冒充管理员、站长或官方身份。"""
    compact = re.sub(r'\s+', '', str(nickname or '')).lower()
    if not compact:
        return False
    return any(name in compact for name in RESERVED_AUTHOR_NAMES)


def fingerprint_from_request(request):
    """清洗并哈希客户端指纹，缺失时用 IP 与 UA 作为降级去重依据。"""
    raw_fingerprint = clean_str(request.data.get('client_fingerprint'), 128).lower()
    ip_address = get_client_ip(request)
    user_agent = clean_str(request.META.get('HTTP_USER_AGENT'), 500)
    return hash_client_fingerprint(raw_fingerprint, settings.SECRET_KEY, f'{ip_address}:{user_agent}'), ip_address, user_agent


def like_target(request, target_type, target):
    """为文章或作品点赞，使用唯一约束防止同一指纹重复点赞。"""
    if target_type not in LIKE_TARGETS:
        return Response({'detail': '点赞目标无效'}, status=400)
    fingerprint, ip_address, user_agent = fingerprint_from_request(request)
    if not fingerprint:
        return Response({'detail': '客户端指纹无效，请刷新后重试'}, status=400)
    recent_ip_count = ContentLike.objects.filter(
        target_type=target_type,
        target_id=target.id,
        ip_address=ip_address,
        created_at__gte=timezone.now() - timedelta(minutes=5),
    ).count()
    if recent_ip_count >= 5:
        return Response({'detail': '点赞过于频繁，请稍后再试', 'like_count': target.like_count}, status=429)
    client = detect_client_info(user_agent)
    try:
        with transaction.atomic():
            ContentLike.objects.create(
                target_type=target_type,
                target_id=target.id,
                fingerprint_hash=fingerprint,
                ip_address=ip_address,
                browser=client['browser'],
                os_name=client['os'],
                device_type=client['device'],
                user_agent=client['user_agent'],
            )
    except IntegrityError:
        target.refresh_from_db(fields=['like_count'])
        return Response({'detail': '已经点赞过啦', 'like_count': target.like_count}, status=400)

    target.__class__.objects.filter(id=target.id).update(like_count=F('like_count') + 1)
    target.refresh_from_db(fields=['like_count'])
    return Response({'detail': '点赞成功', 'like_count': target.like_count})


def settings_map():
    """返回站点设置字典。"""
    return get_site_settings_cached()


def ensure_site_settings(values=None):
    """补齐站点设置。"""
    data = dict(DEFAULT_SITE_SETTINGS)
    if values:
        data.update(values)
    for key, value in data.items():
        SiteSetting.objects.update_or_create(key=key, defaults={'value': value})
    refresh_site_runtime_cache()


def create_default_hello_article(user):
    """初始化后创建第一篇默认文章。"""
    if Article.objects.filter(slug='hello-cpycms').exists():
        return

    category = Category.objects.filter(slug='project-logs').first() or Category.objects.order_by('sort_order', 'id').first()
    tags = list(Tag.objects.filter(name__in=['Django', 'Vue.js', 'Python']))
    article = Article.objects.create(
        title='Hello CPYCMS',
        slug='hello-cpycms',
        summary='CPYCMS 初始化后自动创建的第一篇文章，可在后台文章管理中编辑或删除。',
        content=(
            '# Hello CPYCMS\n\n'
            '欢迎使用 CPYCMS。这是系统初始化后自动创建的第一篇文章，可用于验证 Markdown、图表、公式和代码高亮能力。\n\n'
            '你可以进入后台 **文章管理** 编辑、归档或删除它，也可以直接开始编写自己的 Markdown 内容。\n\n'
            '## Markdown 能力\n\n'
            '- 支持标题、列表、引用和代码块\n'
            '- 支持 Mermaid 图表\n'
            '- 支持 KaTeX 数学公式，例如 $E = mc^2$\n'
            '- 支持代码高亮\n\n'
            '```mermaid\n'
            'graph TD\n'
            '  A[初始化站点] --> B[创建分类和标签]\n'
            '  B --> C[发布 Hello CPYCMS]\n'
            '  C --> D[开始管理内容]\n'
            '```\n\n'
            '```python\n'
            'print("Hello CPYCMS")\n'
            '```\n'
        ),
        category=category,
        author=user,
        status='published',
        is_top=True,
        published_at=timezone.now(),
    )
    if tags:
        article.tags.set(tags)


def category_counts():
    """聚合分类文章数。"""
    rows = Article.objects.filter(category_id__isnull=False).values('category_id').annotate(count=Count('id'))
    return {row['category_id']: row['count'] for row in rows}


def tag_counts():
    """聚合标签文章数。"""
    rows = Tag.objects.annotate(count=Count('articles')).values_list('id', 'count')
    return dict(rows)


def site_bootstrap_payload():
    """返回前台启动数据。"""
    c_counts = category_counts()
    t_counts = tag_counts()
    return {
        'info': settings_map(),
        'categories': [category_dict(item, c_counts.get(item.id, 0)) for item in Category.objects.filter(is_visible=True).order_by('sort_order', 'id')],
        'tags': [tag_dict(item, t_counts.get(item.id, 0)) for item in Tag.objects.order_by('name')],
    }


def parse_nullable_int(value):
    """解析可空整数。"""
    if value in (None, '', 0, '0'):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_status(value, allowed, default):
    """校验状态。"""
    status = clean_str(value, 20) or default
    return status if status in allowed else default


def unique_slug(model, raw_slug, fallback):
    """生成唯一 slug。"""
    base = slugify(clean_str(raw_slug, 200), allow_unicode=False) or fallback
    slug = base
    index = 2
    while model.objects.filter(slug=slug).exists():
        slug = f'{base}-{index}'
        index += 1
    return slug


def normalize_setting(key, value):
    """清洗站点设置。"""
    if key in {'site_logo', 'author_avatar'}:
        text = clean_str(value, 256)
        if text and not text.startswith('/uploads/'):
            raise ValueError('图片路径必须来自本地上传目录')
        if re.search(r'[\x00-\x1f\x7f<>"`\\]', text):
            raise ValueError('图片路径包含非法字符')
        return text
    if key == 'footer_height':
        height = clean_str(value, 20)
        if height not in {'compact', 'normal', 'large'}:
            raise ValueError('页脚高度参数无效')
        return height
    if key in {'theme_primary_color', 'theme_accent_color'}:
        color = clean_str(value, 20)
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError('主题颜色必须是 #RRGGBB 格式')
        return color
    if key in {'icp_beian_number', 'police_beian_number'}:
        text = clean_str(value, 120)
        if re.search(r'[\x00-\x1f\x7f<>"`\\]', text):
            raise ValueError('备案号不能包含 HTML 或脚本危险字符')
        return text
    if key == 'bound_domains':
        text = clean_str(value, 2000)
        if re.search(r'[\x00-\x1f\x7f<>"`\\]', text):
            raise ValueError('绑定域名不能包含 HTML 或脚本危险字符')
        origins = sorted(parse_bound_origins(text))
        if len(origins) > 20:
            raise ValueError('绑定域名最多支持 20 个')
        return '\n'.join(origins)
    if key in {'friend_links', 'hero_slides'}:
        raw = clean_str(value, 10000)
        if raw:
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                raise ValueError('配置必须是 JSON 数组')
            for item in parsed:
                if not isinstance(item, dict):
                    raise ValueError('配置项必须是对象')
                url = clean_str(item.get('url') or item.get('ctaLink'), 500)
                if url and not (url.startswith('/') or url.startswith('https://') or url.startswith('http://')):
                    raise ValueError('链接地址格式无效')
                if key == 'hero_slides' and url and not url.startswith('/'):
                    raise ValueError('首页按钮链接只能使用站内路径')
                if url.lower().startswith(('javascript:', 'data:', 'file:')):
                    raise ValueError('链接协议不安全')
        return raw
    return clean_str(value, 20000 if key == 'about_content' else 1000)


def paged_response(page_data, serializer):
    """序列化分页数据。"""
    return Response({
        'count': page_data['count'],
        'next': page_data['next'],
        'previous': page_data['previous'],
        'page': page_data['page'],
        'page_size': page_data['page_size'],
        'total_pages': page_data['total_pages'],
        'results': [serializer(item) for item in page_data['results']],
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def init_check(_request):
    """检查初始化状态。"""
    return init_state_response()


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def init_setup(request):
    """初始化站点。"""
    if is_initialized():
        return init_state_response(True, status=400, detail='系统已初始化，请勿重复操作')
    try:
        ensure_database_schema()
    except RuntimeError as exc:
        return init_state_response(False, status=409, detail=str(exc))
    username = clean_str(request.data.get('username'), 40)
    password = clean_str(request.data.get('password'), 128)
    if not re.match(r'^[A-Za-z0-9_]{3,40}$', username):
        return init_state_response(False, status=400, detail='用户名只能包含字母、数字和下划线')
    if len(password) < 6:
        return init_state_response(False, status=400, detail='密码至少6个字符')
    User = get_user_model()
    try:
        with transaction.atomic():
            if User.objects.filter(is_active=True).filter(Q(is_superuser=True) | Q(is_staff=True)).exists():
                return init_state_response(True, status=400, detail='系统已初始化，请勿重复操作')
            user = User.objects.create_superuser(username=username, password=password, email=clean_str(request.data.get('author_email'), 120))
            user.nickname = clean_str(request.data.get('author_name'), 80) or username
            user.save(update_fields=['nickname'])
            site_name = clean_str(request.data.get('site_name'), 80) or DEFAULT_SITE_SETTINGS['site_name']
            ensure_site_settings({
                'site_name': site_name,
                'site_slogan': clean_str(request.data.get('site_slogan'), 160),
                'site_description': clean_str(request.data.get('site_description'), 300),
                'author_name': user.nickname,
                'author_email': user.email,
                'banner_title': clean_str(request.data.get('banner_title'), 100) or f'欢迎来到{site_name}',
                'bound_domains': normalize_setting('bound_domains', request.data.get('bound_domains')),
            })
            for item in [
                ('技术笔记', 'tech-notes', '技术学习与探索笔记', 1),
                ('生活随笔', 'life-essays', '生活中的点滴感悟', 2),
                ('项目记录', 'project-logs', '项目开发过程记录', 3),
                ('读书心得', 'reading-notes', '阅读笔记与书评', 4),
            ]:
                Category.objects.get_or_create(name=item[0], defaults={'slug': item[1], 'description': item[2], 'sort_order': item[3]})
            for name, color in [('Python', '#3776ab'), ('Vue.js', '#42b883'), ('Django', '#0c4b33'), ('前端', '#e8654a'), ('随笔', '#8b5cf6')]:
                Tag.objects.get_or_create(name=name, defaults={'color': color})
            create_default_hello_article(user)
    except IntegrityError:
        return init_state_response(is_initialized(), status=400, detail='初始化数据已存在，请刷新后重试')

    if not is_initialized():
        return init_state_response(False, status=500, detail='初始化状态校验失败，请检查数据库写入权限')
    return init_state_response(True, detail='站点初始化成功')


@api_view(['GET'])
def site_info(_request):
    """站点信息。"""
    return Response(settings_map() if is_initialized() else DEFAULT_SITE_SETTINGS)


@api_view(['GET'])
def site_bootstrap(_request):
    """站点启动聚合数据。"""
    if not is_initialized():
        return Response({'initialized': False, 'info': DEFAULT_SITE_SETTINGS, 'categories': [], 'tags': []})
    return Response(site_bootstrap_payload())


@api_view(['GET'])
def categories(_request):
    """前台分类。"""
    counts = category_counts()
    return Response([category_dict(item, counts.get(item.id, 0)) for item in Category.objects.filter(is_visible=True).order_by('sort_order', 'id')])


@api_view(['GET'])
def tags(_request):
    """前台标签。"""
    counts = tag_counts()
    return Response([tag_dict(item, counts.get(item.id, 0)) for item in Tag.objects.order_by('name')])


@api_view(['GET'])
def articles(request):
    """前台文章列表。"""
    queryset = Article.objects.filter(status='published').select_related('category').prefetch_related('tags').defer('content')
    category_id = parse_nullable_int(request.query_params.get('category_id'))
    tag_id = parse_nullable_int(request.query_params.get('tag_id'))
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if tag_id:
        queryset = queryset.filter(tags__id=tag_id)
    queryset = apply_keyword_filter(queryset, ['title', 'summary', 'content'], request.query_params.get('keyword'))
    queryset = queryset.order_by('-is_top', '-published_at', '-id').distinct()
    return paged_response(paginate_queryset(queryset, request, 10), lambda item: article_dict(item, brief=True))


@api_view(['GET'])
def article_search(request):
    """文章搜索。"""
    queryset = Article.objects.filter(status='published').select_related('category').prefetch_related('tags').defer('content')
    queryset = apply_keyword_filter(queryset, ['title', 'summary', 'content'], request.query_params.get('keyword'))
    limit = min(max(int(request.query_params.get('limit', 8) or 8), 1), 20)
    return Response({'keyword': ' '.join(normalize_search_query(request.query_params.get('keyword'))), 'results': [article_dict(item, brief=True) for item in queryset.order_by('-is_top', '-published_at')[:limit]]})


@api_view(['GET'])
def article_detail(_request, slug):
    """文章详情。"""
    article = get_object_or_404(Article.objects.select_related('category').prefetch_related('tags'), slug=slug, status='published')
    Article.objects.filter(id=article.id).update(view_count=F('view_count') + 1)
    article.view_count += 1
    return Response(article_dict(article))


@api_view(['GET'])
def article_hot(_request):
    """热门文章。"""
    queryset = Article.objects.filter(status='published').select_related('category').prefetch_related('tags').order_by('-view_count')[:5]
    return Response([article_dict(item, brief=True) for item in queryset])


@api_view(['POST'])
@authentication_classes([])
def article_like(request, slug):
    """文章点赞。"""
    article = get_object_or_404(Article, slug=slug, status='published')
    return like_target(request, 'article', article)


@api_view(['GET'])
def article_comments(request, slug):
    """文章评论列表；管理员可看到待审评论和管理字段。"""
    article = get_object_or_404(Article, slug=slug, status='published')
    queryset = ArticleComment.objects.filter(article=article).select_related('article').order_by('-created_at')
    if is_admin_user(request):
        return paged_response(paginate_queryset(queryset, request, 12), admin_comment_dict)
    queryset = queryset.filter(is_approved=True)
    return paged_response(paginate_queryset(queryset, request, 12), public_comment_dict)


@api_view(['POST'])
def article_comment_create(request, slug):
    """提交文章评论。"""
    article = get_object_or_404(Article, slug=slug, status='published')
    ip_address = get_client_ip(request)
    user_agent = clean_str(request.META.get('HTTP_USER_AGENT'), 500)
    client = detect_client_info(user_agent)

    if is_admin_user(request):
        content = normalize_plain_text(request.data.get('content'), 1000)
        if len(content) < 2:
            return Response({'detail': '评论内容至少需要 2 个字符'}, status=400)
        nickname = normalize_plain_text(getattr(request.user, 'nickname', '') or request.user.get_username() or '管理员', 80)
        comment = ArticleComment.objects.create(
            article=article,
            nickname=nickname or '管理员',
            email='',
            content=content,
            author_role='admin',
            ip_address=ip_address,
            browser=client['browser'],
            os_name=client['os'],
            device_type=client['device'],
            user_agent=client['user_agent'],
            is_approved=True,
            approved_at=timezone.now(),
        )
        return Response({'detail': '评论已发布', 'id': comment.id})

    payload, error = validate_comment_payload(request.data)
    if error:
        return Response({'detail': error}, status=400)
    if uses_reserved_author_name(payload['nickname']):
        return Response({'detail': '访客昵称不能使用管理员、站长或官方身份'}, status=400)
    fingerprint = hash_client_fingerprint(payload['client_fingerprint'], settings.SECRET_KEY, f'{ip_address}:{user_agent}')
    recent_count = ArticleComment.objects.filter(created_at__gte=timezone.now() - timedelta(minutes=5)).filter(
        ip_address=ip_address
    ).count()
    if fingerprint:
        recent_count = max(
            recent_count,
            ArticleComment.objects.filter(created_at__gte=timezone.now() - timedelta(minutes=5), fingerprint_hash=fingerprint).count(),
        )
    if recent_count >= 3:
        return Response({'detail': '评论提交过于频繁，请稍后再试'}, status=429)
    comment = ArticleComment.objects.create(
        article=article,
        nickname=payload['nickname'],
        email=payload['email'],
        content=payload['content'],
        author_role='visitor',
        ip_address=ip_address,
        fingerprint_hash=fingerprint,
        browser=client['browser'],
        os_name=client['os'],
        device_type=client['device'],
        user_agent=client['user_agent'],
    )
    return Response({'detail': '评论提交成功，等待审核', 'id': comment.id})


@api_view(['GET'])
def works(request):
    """作品列表。"""
    queryset = Work.objects.filter(status='published').select_related('category').defer('description', 'content')
    category_id = parse_nullable_int(request.query_params.get('category_id'))
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    queryset = apply_keyword_filter(queryset, ['title', 'description', 'content', 'tech_stack'], request.query_params.get('keyword'))
    return paged_response(paginate_queryset(queryset.order_by('sort_order', '-created_at'), request, 12), lambda item: work_dict(item, brief=True))


@api_view(['GET'])
def work_search(request):
    """作品搜索。"""
    queryset = apply_keyword_filter(Work.objects.filter(status='published').select_related('category').defer('description', 'content'), ['title', 'description', 'content', 'tech_stack'], request.query_params.get('keyword'))
    limit = min(max(int(request.query_params.get('limit', 8) or 8), 1), 20)
    return Response({'keyword': ' '.join(normalize_search_query(request.query_params.get('keyword'))), 'results': [work_dict(item, brief=True) for item in queryset.order_by('sort_order', '-created_at')[:limit]]})


@api_view(['GET'])
def work_detail(_request, work_id):
    """作品详情。"""
    work = get_object_or_404(Work.objects.select_related('category'), id=work_id, status='published')
    Work.objects.filter(id=work.id).update(view_count=F('view_count') + 1)
    work.view_count += 1
    return Response(work_dict(work))


@api_view(['POST'])
@authentication_classes([])
def work_like(request, work_id):
    """作品点赞。"""
    work = get_object_or_404(Work, id=work_id, status='published')
    return like_target(request, 'work', work)


@api_view(['GET'])
def resources(request):
    """资源列表。"""
    queryset = apply_keyword_filter(Resource.objects.filter(status='published'), ['title', 'description', 'file_name', 'file_type'], request.query_params.get('keyword'))
    return paged_response(paginate_queryset(queryset.order_by('-download_count', '-created_at'), request, 15), resource_dict)


@api_view(['GET'])
def resource_search(request):
    """资源搜索。"""
    queryset = apply_keyword_filter(Resource.objects.filter(status='published'), ['title', 'description', 'file_name', 'file_type'], request.query_params.get('keyword'))
    limit = min(max(int(request.query_params.get('limit', 8) or 8), 1), 20)
    return Response({'keyword': ' '.join(normalize_search_query(request.query_params.get('keyword'))), 'results': [resource_dict(item) for item in queryset.order_by('-download_count', '-created_at')[:limit]]})


@api_view(['GET'])
def resource_download(_request, resource_id):
    """下载资源。"""
    resource = get_object_or_404(Resource, id=resource_id, status='published')
    if not resource.file_path or not is_path_under(settings.MEDIA_ROOT / 'resources', resource.file_path):
        return Response({'detail': '资源文件路径无效'}, status=404)
    path = Path(resource.file_path)
    if not path.exists():
        return Response({'detail': '资源文件不存在'}, status=404)
    resource.download_count += 1
    resource.save(update_fields=['download_count'])
    return FileResponse(path.open('rb'), as_attachment=True, filename=resource.file_name)


@api_view(['GET'])
def messages(request):
    """公开留言。"""
    queryset = Message.objects.filter(is_approved=True).order_by('-created_at')
    return paged_response(paginate_queryset(queryset, request, 20), message_dict)


@api_view(['POST'])
def message_create(request):
    """提交留言。"""
    admin_message = is_admin_user(request)
    nickname = clean_str(request.data.get('nickname'), 80)
    content = clean_str(request.data.get('content'), 1000)
    if admin_message and not nickname:
        nickname = clean_str(getattr(request.user, 'nickname', '') or request.user.get_username() or '管理员', 80)
    if not nickname or not content:
        return Response({'detail': '请填写昵称和留言内容'}, status=400)
    if not admin_message and uses_reserved_author_name(nickname):
        return Response({'detail': '访客昵称不能使用管理员、站长或官方身份'}, status=400)
    Message.objects.create(
        nickname=nickname,
        email='' if admin_message else clean_str(request.data.get('email'), 120),
        content=content,
        author_role='admin' if admin_message else 'visitor',
        is_approved=admin_message,
        ip_address=get_client_ip(request),
    )
    detail = '留言已发布' if admin_message else '留言成功，等待审核'
    return Response({'detail': detail})


@api_view(['GET'])
@admin_required
def admin_articles(request):
    """后台文章列表。"""
    queryset = Article.objects.select_related('category').prefetch_related('tags')
    status = clean_str(request.query_params.get('status'), 20)
    if status in ARTICLE_STATUS:
        queryset = queryset.filter(status=status)
    queryset = apply_keyword_filter(queryset, ['title'], request.query_params.get('keyword'))
    return paged_response(paginate_queryset(queryset.order_by('-created_at'), request, 15), lambda item: article_dict(item, brief=True))


@api_view(['POST'])
@admin_required
def admin_article_create(request):
    """创建文章。"""
    title = clean_str(request.data.get('title'), 200)
    content = clean_str(request.data.get('content'))
    if not title or not content:
        return Response({'detail': '标题和正文不能为空'}, status=400)
    status = parse_status(request.data.get('status'), ARTICLE_STATUS, 'draft')
    article = Article.objects.create(
        title=title,
        slug=unique_slug(Article, request.data.get('slug') or title, f'article-{timezone.now().strftime("%Y%m%d%H%M%S")}'),
        summary=clean_str(request.data.get('summary'), 300),
        content=content,
        category_id=parse_nullable_int(request.data.get('category_id')),
        author=request.user,
        status=status,
        cover_image=clean_str(request.data.get('cover_image'), 256),
        is_top=bool(request.data.get('is_top', False)),
        published_at=timezone.now() if status == 'published' else None,
    )
    tag_ids = request.data.get('tag_ids') or []
    if tag_ids:
        article.tags.set(Tag.objects.filter(id__in=tag_ids))
    return Response(article_dict(article))


@api_view(['GET', 'PUT', 'DELETE'])
@admin_required
def admin_article_detail(request, article_id):
    """后台文章详情、更新、删除。"""
    article = get_object_or_404(Article.objects.select_related('category').prefetch_related('tags'), id=article_id)
    if request.method == 'GET':
        return Response(article_dict(article))
    if request.method == 'DELETE':
        article.delete()
        return Response({'detail': '文章已删除'})
    data = request.data
    if 'title' in data:
        article.title = clean_str(data.get('title'), 200)
    if 'slug' in data:
        new_slug = clean_str(data.get('slug'), 200)
        if new_slug and Article.objects.exclude(id=article.id).filter(slug=new_slug).exists():
            return Response({'detail': 'URL别名已存在'}, status=400)
        article.slug = new_slug or article.slug
    if 'content' in data:
        article.content = clean_str(data.get('content'))
    if 'summary' in data:
        article.summary = clean_str(data.get('summary'), 300)
    if 'category_id' in data:
        article.category_id = parse_nullable_int(data.get('category_id'))
    if 'cover_image' in data:
        article.cover_image = clean_str(data.get('cover_image'), 256)
    if 'is_top' in data:
        article.is_top = bool(data.get('is_top'))
    if 'status' in data:
        old_status = article.status
        article.status = parse_status(data.get('status'), ARTICLE_STATUS, article.status)
        if article.status == 'published' and old_status != 'published':
            article.published_at = timezone.now()
    article.save()
    if 'tag_ids' in data:
        article.tags.set(Tag.objects.filter(id__in=data.get('tag_ids') or []))
    return Response(article_dict(article))


@api_view(['GET', 'POST'])
@admin_required
def admin_categories(request):
    """分类管理。"""
    if request.method == 'GET':
        counts = category_counts()
        return Response([category_dict(item, counts.get(item.id, 0)) for item in Category.objects.order_by('sort_order', 'id')])
    name = clean_str(request.data.get('name'), 50)
    if not name:
        return Response({'detail': '分类名称不能为空'}, status=400)
    category = Category.objects.create(
        name=name,
        slug=unique_slug(Category, request.data.get('slug') or name, f'cat-{timezone.now().strftime("%Y%m%d%H%M%S")}'),
        description=clean_str(request.data.get('description'), 200),
        sort_order=int(request.data.get('sort_order') or 0),
        is_visible=bool(request.data.get('is_visible', True)),
    )
    return Response(category_dict(category))


@api_view(['PUT', 'DELETE'])
@admin_required
def admin_category_detail(request, category_id):
    """分类更新删除。"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'DELETE':
        if category.articles.exists() or category.works.exists():
            return Response({'detail': '该分类下还有内容，无法删除'}, status=400)
        category.delete()
        return Response({'detail': '分类已删除'})
    for field in ['name', 'description']:
        if field in request.data:
            setattr(category, field, clean_str(request.data.get(field), 200))
    if 'slug' in request.data:
        category.slug = clean_str(request.data.get('slug'), 50)
    if 'sort_order' in request.data:
        category.sort_order = int(request.data.get('sort_order') or 0)
    if 'is_visible' in request.data:
        category.is_visible = bool(request.data.get('is_visible'))
    category.save()
    return Response(category_dict(category, category.articles.count()))


@api_view(['GET', 'POST'])
@admin_required
def admin_tags(request):
    """标签管理。"""
    if request.method == 'GET':
        counts = tag_counts()
        return Response([tag_dict(item, counts.get(item.id, 0)) for item in Tag.objects.order_by('name')])
    name = clean_str(request.data.get('name'), 50)
    if not name:
        return Response({'detail': '标签名不能为空'}, status=400)
    color = clean_str(request.data.get('color'), 20) or '#0d4f56'
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return Response({'detail': '标签颜色必须是 #RRGGBB 格式'}, status=400)
    if Tag.objects.filter(name=name).exists():
        return Response({'detail': '标签已存在'}, status=400)
    tag = Tag.objects.create(name=name, color=color)
    return Response(tag_dict(tag))


@api_view(['PUT', 'DELETE'])
@admin_required
def admin_tag_detail(request, tag_id):
    """更新或删除标签。"""
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == 'DELETE':
        tag.delete()
        return Response({'detail': '标签已删除'})

    if 'name' in request.data:
        name = clean_str(request.data.get('name'), 50)
        if not name:
            return Response({'detail': '标签名不能为空'}, status=400)
        if Tag.objects.exclude(id=tag.id).filter(name=name).exists():
            return Response({'detail': '标签已存在'}, status=400)
        tag.name = name
    if 'color' in request.data:
        color = clean_str(request.data.get('color'), 20) or '#0d4f56'
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return Response({'detail': '标签颜色必须是 #RRGGBB 格式'}, status=400)
        tag.color = color
    tag.save()
    return Response(tag_dict(tag, tag.articles.count()))


@api_view(['GET', 'POST'])
@admin_required
def admin_works(request):
    """作品管理。"""
    if request.method == 'GET':
        return paged_response(paginate_queryset(Work.objects.select_related('category').order_by('-created_at'), request, 15), lambda item: work_dict(item, brief=True))
    title = clean_str(request.data.get('title'), 200)
    if not title:
        return Response({'detail': '作品名称不能为空'}, status=400)
    stack = request.data.get('tech_stack') or ''
    if isinstance(stack, list):
        stack = ','.join(stack)
    work = Work.objects.create(
        title=title,
        description=clean_str(request.data.get('description')),
        content=clean_str(request.data.get('content')),
        cover_image=clean_str(request.data.get('cover_image'), 256),
        category_id=parse_nullable_int(request.data.get('category_id')),
        tech_stack=clean_str(stack, 500),
        demo_url=clean_str(request.data.get('demo_url'), 500),
        source_url=clean_str(request.data.get('source_url'), 500),
        status=parse_status(request.data.get('status'), PUBLIC_STATUS, 'published'),
        sort_order=int(request.data.get('sort_order') or 0),
    )
    return Response(work_dict(work))


@api_view(['PUT', 'DELETE'])
@admin_required
def admin_work_detail(request, work_id):
    """作品更新删除。"""
    work = get_object_or_404(Work, id=work_id)
    if request.method == 'DELETE':
        work.delete()
        return Response({'detail': '作品已删除'})
    for field in ['title', 'description', 'content', 'cover_image', 'demo_url', 'source_url']:
        if field in request.data:
            setattr(work, field, clean_str(request.data.get(field), 500))
    if 'category_id' in request.data:
        work.category_id = parse_nullable_int(request.data.get('category_id'))
    if 'tech_stack' in request.data:
        stack = request.data.get('tech_stack') or ''
        work.tech_stack = ','.join(stack) if isinstance(stack, list) else clean_str(stack, 500)
    if 'status' in request.data:
        work.status = parse_status(request.data.get('status'), PUBLIC_STATUS, work.status)
    if 'sort_order' in request.data:
        work.sort_order = int(request.data.get('sort_order') or 0)
    work.save()
    return Response(work_dict(work))


@api_view(['GET', 'POST'])
@admin_required
def admin_resources(request):
    """资源管理。"""
    if request.method == 'GET':
        queryset = Resource.objects.all()
        status = clean_str(request.query_params.get('status'), 20)
        if status in PUBLIC_STATUS:
            queryset = queryset.filter(status=status)
        queryset = apply_keyword_filter(queryset, ['title', 'description', 'file_name', 'file_type'], request.query_params.get('keyword'))
        return paged_response(paginate_queryset(queryset.order_by('-download_count', '-created_at'), request, 15), resource_dict)
    title = clean_str(request.data.get('title'), 200)
    file_obj = request.FILES.get('file')
    ok, message = validate_upload(file_obj, settings.ALLOWED_RESOURCE_EXT)
    if not title or not ok:
        return Response({'detail': message or '资源名称不能为空'}, status=400)
    path, _url = save_upload(file_obj, 'resources')
    resource = Resource.objects.create(
        title=title,
        description=clean_str(request.data.get('description'), 2000),
        file_path=path,
        file_name=os.path.basename(file_obj.name)[:200],
        file_size=file_obj.size,
        file_type=file_obj.name.rsplit('.', 1)[1].lower(),
        status=parse_status(request.data.get('status'), PUBLIC_STATUS, 'published'),
    )
    return Response(resource_dict(resource))


@api_view(['PUT', 'DELETE'])
@admin_required
def admin_resource_detail(request, resource_id):
    """资源更新删除。"""
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == 'DELETE':
        if resource.file_path and is_path_under(settings.MEDIA_ROOT / 'resources', resource.file_path) and Path(resource.file_path).exists():
            Path(resource.file_path).unlink()
        resource.delete()
        return Response({'detail': '资源已删除'})
    if 'title' in request.data:
        resource.title = clean_str(request.data.get('title'), 200)
    if 'description' in request.data:
        resource.description = clean_str(request.data.get('description'), 2000)
    if 'status' in request.data:
        resource.status = parse_status(request.data.get('status'), PUBLIC_STATUS, resource.status)
    resource.save()
    return Response(resource_dict(resource))


@api_view(['GET'])
@admin_required
def admin_messages(request):
    """后台留言列表。"""
    queryset = Message.objects.all()
    status = clean_str(request.query_params.get('status'), 20)
    if status == 'pending':
        queryset = queryset.filter(is_approved=False)
    elif status == 'approved':
        queryset = queryset.filter(is_approved=True)
    return paged_response(paginate_queryset(queryset.order_by('-created_at'), request, 20), lambda item: message_dict(item, include_private=True))


@api_view(['PUT'])
@admin_required
def admin_message_approve(_request, message_id):
    """审核留言。"""
    message = get_object_or_404(Message, id=message_id)
    message.is_approved = True
    message.save(update_fields=['is_approved'])
    return Response({'detail': '留言已审核'})


@api_view(['PUT'])
@admin_required
def admin_message_reply(request, message_id):
    """回复留言。"""
    message = get_object_or_404(Message, id=message_id)
    message.reply = clean_str(request.data.get('reply'), 1000)
    message.is_replied = bool(message.reply)
    message.replied_at = timezone.now() if message.reply else None
    message.is_approved = True
    message.save()
    return Response({'detail': '回复已保存'})


@api_view(['DELETE'])
@admin_required
def admin_message_delete(_request, message_id):
    """删除留言。"""
    get_object_or_404(Message, id=message_id).delete()
    return Response({'detail': '留言已删除'})


@api_view(['GET'])
@admin_required
def admin_comments(request):
    """后台评论列表。"""
    queryset = ArticleComment.objects.select_related('article')
    status = clean_str(request.query_params.get('status'), 20)
    if status == 'pending':
        queryset = queryset.filter(is_approved=False)
    elif status == 'approved':
        queryset = queryset.filter(is_approved=True)
    return paged_response(paginate_queryset(queryset.order_by('-created_at'), request, 20), admin_comment_dict)


@api_view(['PUT'])
@admin_required
def admin_comment_approve(_request, comment_id):
    """审核评论。"""
    comment = get_object_or_404(ArticleComment, id=comment_id)
    comment.is_approved = True
    comment.approved_at = timezone.now()
    comment.save(update_fields=['is_approved', 'approved_at'])
    return Response({'detail': '评论已审核'})


@api_view(['PUT'])
@admin_required
def admin_comment_reply(request, comment_id):
    """回复文章评论。"""
    comment = get_object_or_404(ArticleComment, id=comment_id)
    comment.reply = clean_str(request.data.get('reply'), 1000)
    comment.is_replied = bool(comment.reply)
    comment.replied_at = timezone.now() if comment.reply else None
    comment.is_approved = True
    if comment.approved_at is None:
        comment.approved_at = timezone.now()
    comment.save(update_fields=['reply', 'is_replied', 'replied_at', 'is_approved', 'approved_at'])
    return Response({'detail': '回复已保存'})


@api_view(['DELETE'])
@admin_required
def admin_comment_delete(_request, comment_id):
    """删除评论。"""
    get_object_or_404(ArticleComment, id=comment_id).delete()
    return Response({'detail': '评论已删除'})


def _handle_image_upload(request, subdir):
    """执行图片上传。"""
    file_obj = request.FILES.get('image')
    ok, message = validate_upload(file_obj, settings.ALLOWED_IMAGE_EXT)
    if not ok:
        return Response({'detail': message}, status=400)
    path, url = save_upload(file_obj, subdir)
    return Response({'url': url, 'filename': os.path.basename(path)})


@api_view(['POST'])
@admin_required
def upload_image(request):
    """上传文章正文图片。"""
    return _handle_image_upload(request, 'articles')


@api_view(['POST'])
@admin_required
def upload_article_cover(request):
    """上传文章封面。"""
    return _handle_image_upload(request, 'articles')


@api_view(['POST'])
@admin_required
def upload_work_cover(request):
    """上传作品封面。"""
    return _handle_image_upload(request, 'works')


@api_view(['POST'])
@admin_required
def upload_site_logo(request):
    """上传站点 Logo。"""
    return _handle_image_upload(request, 'site')


@api_view(['GET', 'PUT'])
@admin_required
def admin_settings(request):
    """站点设置管理。"""
    if request.method == 'GET':
        return Response(settings_map())
    allowed = set(DEFAULT_SITE_SETTINGS.keys())
    for key, value in request.data.items():
        if key not in allowed:
            continue
        try:
            normalized = normalize_setting(key, value)
        except (ValueError, json.JSONDecodeError) as exc:
            return Response({'detail': str(exc)}, status=400)
        SiteSetting.objects.update_or_create(key=key, defaults={'value': normalized})
    refresh_site_runtime_cache()
    return Response({'detail': '设置已保存'})


@api_view(['GET'])
@admin_required
def admin_stats(_request):
    """后台统计。"""
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    qs = Article.objects.filter(created_at__date__gte=seven_days_ago).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id'))
    counts_by_date = {str(item['date']): item['count'] for item in qs}
    
    daily = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        daily.append({'date': day.isoformat(), 'count': counts_by_date.get(str(day), 0)})
    return Response({
        'article_count': Article.objects.count(),
        'published_count': Article.objects.filter(status='published').count(),
        'draft_count': Article.objects.filter(status='draft').count(),
        'work_count': Work.objects.count(),
        'resource_count': Resource.objects.count(),
        'message_count': Message.objects.count(),
        'pending_messages': Message.objects.filter(is_approved=False).count(),
        'comment_count': ArticleComment.objects.count(),
        'pending_comments': ArticleComment.objects.filter(is_approved=False).count(),
        'category_count': Category.objects.count(),
        'total_views': Article.objects.aggregate(value=Sum('view_count'))['value'] or 0,
        'total_likes': (Article.objects.aggregate(value=Sum('like_count'))['value'] or 0) + (Work.objects.aggregate(value=Sum('like_count'))['value'] or 0),
        'total_downloads': Resource.objects.aggregate(value=Sum('download_count'))['value'] or 0,
        'daily_articles': daily,
        'category_distribution': [
            {'name': item.name, 'count': item.article_count}
            for item in Category.objects.annotate(article_count=Count('articles'))
        ],
        'top_articles': [
            {'title': item.title, 'views': item.view_count}
            for item in Article.objects.order_by('-view_count')[:5]
        ],
    })
