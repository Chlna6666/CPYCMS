# -*- coding: utf-8 -*-
"""CPYCMS - 文章评论安全清洗与客户端信息识别。"""

import hashlib
import re


EMAIL_PATTERN = re.compile(r'^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,20}$')
FINGERPRINT_PATTERN = re.compile(r'^[a-f0-9]{32,128}$')


def normalize_plain_text(value, max_len):
    """清洗访客提交的纯文本，移除控制字符和 HTML 标签。"""
    text = str(value or '').strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>\n]{0,200}>', '', text)
    text = text.replace('<', '').replace('>', '')
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text[:max_len]


def validate_comment_payload(data):
    """校验文章评论入参，邮箱为必填。"""
    raw_nickname = str(data.get('nickname') or '').strip()
    raw_email = str(data.get('email') or '').strip()
    raw_content = str(data.get('content') or '').strip()

    if len(raw_nickname) > 40:
        return None, '昵称不能超过 40 个字符'
    if len(raw_email) > 120:
        return None, '邮箱不能超过 120 个字符'
    if len(raw_content) > 1000:
        return None, '评论内容不能超过 1000 字'

    nickname = normalize_plain_text(data.get('nickname'), 40)
    email = normalize_plain_text(data.get('email'), 120).lower()
    content = normalize_plain_text(data.get('content'), 1000)
    fingerprint = str(data.get('client_fingerprint') or '').strip().lower()[:128]

    if len(nickname) < 2:
        return None, '昵称至少需要 2 个字符'
    if not EMAIL_PATTERN.match(email):
        return None, '邮箱格式不正确'
    if len(content) < 2:
        return None, '评论内容至少需要 2 个字符'
    if fingerprint and not FINGERPRINT_PATTERN.match(fingerprint):
        fingerprint = ''

    return {
        'nickname': nickname,
        'email': email,
        'content': content,
        'client_fingerprint': fingerprint,
    }, ''


def hash_client_fingerprint(raw_fingerprint, secret_key, fallback=''):
    """使用服务端密钥二次哈希指纹，不保存浏览器原始指纹。"""
    raw = raw_fingerprint or fallback
    if not raw:
        return ''
    payload = f'{secret_key or "cpycms"}:{raw}'.encode('utf-8', 'ignore')
    return hashlib.sha256(payload).hexdigest()


def detect_client_info(user_agent):
    """从 User-Agent 识别浏览器、系统和设备类型。"""
    ua = (user_agent or '')[:500]
    lower = ua.lower()

    if 'edg/' in lower:
        browser = 'Edge'
    elif 'firefox/' in lower:
        browser = 'Firefox'
    elif 'chrome/' in lower or 'crios/' in lower:
        browser = 'Chrome'
    elif 'safari/' in lower:
        browser = 'Safari'
    elif 'micromessenger' in lower:
        browser = 'WeChat'
    else:
        browser = 'Unknown'

    if 'windows nt' in lower:
        os_name = 'Windows'
    elif 'android' in lower:
        os_name = 'Android'
    elif 'iphone' in lower or 'ipad' in lower or 'ios' in lower:
        os_name = 'iOS'
    elif 'mac os x' in lower or 'macintosh' in lower:
        os_name = 'macOS'
    elif 'linux' in lower:
        os_name = 'Linux'
    else:
        os_name = 'Unknown'

    if 'ipad' in lower or 'tablet' in lower:
        device = 'Tablet'
    elif 'mobile' in lower or 'iphone' in lower or 'android' in lower:
        device = 'Mobile'
    else:
        device = 'Desktop'

    return {'browser': browser, 'os': os_name, 'device': device, 'user_agent': ua}
