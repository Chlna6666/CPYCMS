# -*- coding: utf-8 -*-
"""CPYCMS - API 序列化函数。"""

from backend.apps.cms.models import Article, ArticleComment, Category, Message, Resource, Tag, Work


def dt(value):
    """格式化时间。"""
    return value.strftime('%Y-%m-%d %H:%M:%S') if value else ''


def category_dict(category: Category, article_count=0):
    """分类序列化。"""
    return {
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'description': category.description,
        'sort_order': category.sort_order,
        'is_visible': category.is_visible,
        'article_count': int(article_count or 0),
        'created_at': dt(category.created_at),
    }


def tag_dict(tag: Tag, article_count=0):
    """标签序列化。"""
    return {
        'id': tag.id,
        'name': tag.name,
        'color': tag.color,
        'article_count': int(article_count or 0),
    }


def article_dict(article: Article, brief=False):
    """文章序列化。"""
    data = {
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.summary,
        'cover_image': article.cover_image,
        'category_id': article.category_id,
        'category_name': article.category.name if article.category else '',
        'author_id': article.author_id,
        'status': article.status,
        'view_count': article.view_count,
        'like_count': article.like_count,
        'is_top': article.is_top,
        'created_at': dt(article.created_at),
        'published_at': dt(article.published_at),
        'tags': [{'id': tag.id, 'name': tag.name} for tag in article.tags.all()],
    }
    if not brief:
        data['content'] = article.content
        data['updated_at'] = dt(article.updated_at)
    return data


def work_dict(work: Work, brief=False):
    """作品序列化。"""
    data = {
        'id': work.id,
        'title': work.title,
        'description': work.description,
        'cover_image': work.cover_image,
        'category_id': work.category_id,
        'category_name': work.category.name if work.category else '',
        'tech_stack': [item for item in work.tech_stack.split(',') if item] if work.tech_stack else [],
        'demo_url': work.demo_url,
        'source_url': work.source_url,
        'status': work.status,
        'like_count': work.like_count,
        'view_count': work.view_count,
        'sort_order': work.sort_order,
        'created_at': dt(work.created_at),
    }
    if not brief:
        data['content'] = work.content
        data['updated_at'] = dt(work.updated_at)
    return data


def resource_dict(resource: Resource):
    """资源序列化。"""
    return {
        'id': resource.id,
        'title': resource.title,
        'description': resource.description,
        'file_name': resource.file_name,
        'file_size': resource.file_size,
        'file_type': resource.file_type,
        'download_count': resource.download_count,
        'status': resource.status,
        'created_at': dt(resource.created_at),
        'updated_at': dt(resource.updated_at),
    }


def message_dict(message: Message, include_private=False):
    """留言序列化；公开列表不返回邮箱和 IP。"""
    data = {
        'id': message.id,
        'nickname': message.nickname,
        'content': message.content,
        'reply': message.reply,
        'author_role': message.author_role,
        'is_admin_author': message.author_role == 'admin',
        'is_approved': message.is_approved,
        'is_replied': message.is_replied,
        'created_at': dt(message.created_at),
        'replied_at': dt(message.replied_at),
    }
    if include_private:
        data.update({
            'email': message.email,
            'ip_address': message.ip_address,
        })
    return data


def mask_email(email):
    """脱敏邮箱。"""
    if not email or '@' not in email:
        return ''
    prefix, domain = email.split('@', 1)
    shown = prefix[:2] if len(prefix) > 2 else prefix[:1]
    return f'{shown}***@{domain}'


def public_comment_dict(comment: ArticleComment):
    """公开评论序列化。"""
    return {
        'id': comment.id,
        'article_id': comment.article_id,
        'nickname': comment.nickname,
        'email_masked': mask_email(comment.email),
        'content': comment.content,
        'reply': comment.reply,
        'author_role': comment.author_role,
        'is_admin_author': comment.author_role == 'admin',
        'is_replied': comment.is_replied,
        'browser': comment.browser,
        'os_name': comment.os_name,
        'device_type': comment.device_type,
        'created_at': dt(comment.created_at),
        'replied_at': dt(comment.replied_at),
    }


def admin_comment_dict(comment: ArticleComment):
    """后台评论序列化。"""
    data = public_comment_dict(comment)
    data.update({
        'email': comment.email,
        'is_approved': comment.is_approved,
        'ip_address': comment.ip_address,
        'fingerprint_hash': comment.fingerprint_hash[:12] if comment.fingerprint_hash else '',
        'user_agent': comment.user_agent,
        'article_title': comment.article.title if comment.article else '',
        'article_slug': comment.article.slug if comment.article else '',
        'approved_at': dt(comment.approved_at),
    })
    return data
