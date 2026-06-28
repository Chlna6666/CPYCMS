# -*- coding: utf-8 -*-
"""CPYCMS - 认证 URL。"""

from django.urls import path

from backend.apps.accounts import views


urlpatterns = [
    path('csrf/', views.csrf_token),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('session/', views.session_view),
    path('profile/', views.profile_view),
    path('password/', views.password_view),
]
