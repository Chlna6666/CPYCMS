# -*- coding: utf-8 -*-
"""CPYCMS - Django CMS 数据模型。"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """内容分类。"""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, default='')
    sort_order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['is_visible', 'sort_order'], name='idx_categories_visible_sort'),
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """文章标签。"""

    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=20, default='#0d4f56')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    """文章内容。"""

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    summary = models.TextField(blank=True, default='')
    content = models.TextField()
    cover_image = models.CharField(max_length=256, blank=True, default='')
    category = models.ForeignKey(Category, null=True, blank=True, related_name='articles', on_delete=models.SET_NULL)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='articles', on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    is_top = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_top', 'published_at'], name='idx_article_status_top_pub'),
            models.Index(fields=['status', 'category', 'published_at'], name='idx_article_status_cat_pub'),
            models.Index(fields=['created_at', 'status'], name='idx_articles_created_status'),
            models.Index(fields=['view_count'], name='idx_article_view_count'),
        ]

    def __str__(self):
        return self.title


class Work(models.Model):
    """作品展示。"""

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    content = models.TextField(blank=True, default='')
    cover_image = models.CharField(max_length=256, blank=True, default='')
    category = models.ForeignKey(Category, null=True, blank=True, related_name='works', on_delete=models.SET_NULL)
    tech_stack = models.CharField(max_length=500, blank=True, default='')
    demo_url = models.CharField(max_length=500, blank=True, default='')
    source_url = models.CharField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    like_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'works'
        ordering = ['sort_order', '-created_at']
        indexes = [
            models.Index(fields=['status', 'sort_order', 'created_at'], name='idx_works_status_sort_created'),
            models.Index(fields=['status', 'category', 'sort_order'], name='idx_works_status_category_sort'),
        ]

    def __str__(self):
        return self.title


class Resource(models.Model):
    """资源下载。"""

    STATUS_CHOICES = Work.STATUS_CHOICES

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=200)
    file_size = models.IntegerField(default=0)
    file_type = models.CharField(max_length=20, blank=True, default='')
    download_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resources'
        ordering = ['-download_count', '-created_at']
        indexes = [
            models.Index(fields=['status', 'download_count', 'created_at'], name='idx_resource_status_dl_created'),
        ]

    def __str__(self):
        return self.title


class Message(models.Model):
    """留言板。"""

    AUTHOR_ROLE_CHOICES = (
        ('visitor', 'Visitor'),
        ('admin', 'Admin'),
    )

    nickname = models.CharField(max_length=80)
    email = models.CharField(max_length=120, blank=True, default='')
    content = models.TextField()
    reply = models.TextField(blank=True, default='')
    author_role = models.CharField(max_length=20, choices=AUTHOR_ROLE_CHOICES, default='visitor')
    is_approved = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_approved', 'created_at'], name='idx_messages_approved_created'),
        ]


class ArticleComment(models.Model):
    """文章评论。"""

    AUTHOR_ROLE_CHOICES = Message.AUTHOR_ROLE_CHOICES

    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    nickname = models.CharField(max_length=80)
    email = models.CharField(max_length=120)
    content = models.TextField()
    reply = models.TextField(blank=True, default='')
    author_role = models.CharField(max_length=20, choices=AUTHOR_ROLE_CHOICES, default='visitor')
    is_approved = models.BooleanField(default=False, db_index=True)
    is_replied = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=50, blank=True, default='', db_index=True)
    fingerprint_hash = models.CharField(max_length=64, blank=True, default='', db_index=True)
    browser = models.CharField(max_length=80, blank=True, default='')
    os_name = models.CharField(max_length=80, blank=True, default='')
    device_type = models.CharField(max_length=40, blank=True, default='')
    user_agent = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'article_comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'is_approved', 'created_at'], name='idx_comment_art_appr_crt'),
        ]


class ContentLike(models.Model):
    """文章与作品点赞记录，用服务端哈希后的指纹做去重。"""

    TARGET_CHOICES = (
        ('article', 'Article'),
        ('work', 'Work'),
    )

    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_id = models.IntegerField()
    fingerprint_hash = models.CharField(max_length=64)
    ip_address = models.CharField(max_length=50, blank=True, default='')
    browser = models.CharField(max_length=80, blank=True, default='')
    os_name = models.CharField(max_length=80, blank=True, default='')
    device_type = models.CharField(max_length=40, blank=True, default='')
    user_agent = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'content_likes'
        indexes = [
            models.Index(fields=['target_type', 'target_id'], name='idx_likes_target'),
            models.Index(fields=['fingerprint_hash', 'created_at'], name='idx_likes_fp_created'),
            models.Index(fields=['ip_address', 'created_at'], name='idx_likes_ip_created'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['target_type', 'target_id', 'fingerprint_hash'], name='uq_like_target_fp'),
        ]


class SiteSetting(models.Model):
    """站点设置。"""

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'site_settings'


class VisitLog(models.Model):
    """访问日志。"""

    ip_address = models.CharField(max_length=50, blank=True, default='')
    path = models.CharField(max_length=500, blank=True, default='')
    user_agent = models.CharField(max_length=500, blank=True, default='')
    visit_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'visit_logs'
