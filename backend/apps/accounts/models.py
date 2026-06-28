# -*- coding: utf-8 -*-
"""CPYCMS - Django 用户模型。"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """管理员用户。"""

    nickname = models.CharField(max_length=80, blank=True, default='')
    avatar = models.CharField(max_length=256, blank=True, default='')
    bio = models.TextField(blank=True, default='')

    def display_name(self):
        """返回后台展示名称。"""
        return self.nickname or self.username
