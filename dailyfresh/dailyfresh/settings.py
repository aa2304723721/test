"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't86*&u31rliheqh6(kq$l=s4+s3yk5v0e66--vl8*zx9gs#6+='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',  # 富文本编辑器
    'user',  # 用户模块
    'goods',  # 商品模块
    'cart',  # 购物车模块
    'order',  # 订单模块
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'USER': 'root',
        'PASSWORD': '10.',
        'HOST': '192.168.12.232',
        'PORT': 3306,
    }
}

# django认证系统使用的模型类
AUTH_USER_MODEL = 'user.User'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# 富文本编辑器配置
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400,
}


# 配置session储存到redis
SESSION_ENGINE = "redis_sessions.session"
SESSION_REDIS_HOST = "192.168.12.232"
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 2
SESSION_REDIS_PASSWORD = ""
SESSION_REDIS_PREFIX = "session"




# 发送邮件配置
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
# smpt服务地址
EMAIL_HOST='smtp.163.com'
EMAIL_PORT=25
# 发送邮件的邮箱
EMAIL_HOST_USER='z31926990@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD='z17025'
# 收件人看到的发件人
EMAIL_FROM='天天生鲜<z31926990@163.com>'

# Django的缓存配置
# CACHES = {
#     "default": {
#         "BACKEND":"django_redis.cache.RedisCache",
#         "LOCATION": "redis://192.168.12.232:6379/2",
#         "OPTIONS": {
#             "CLIENT_CLASS":"django_redis.client.DefaultClient",
#         }
#
#     }
# }

# 配置登录url地址
LOGIN_URL='/user/login'

# 设置Django的文件存储类
DEFAULT_FILE_STORAGE="utils.fdfs.storage.FDFSStorage"


# 设置fdfs使用的client.conf路径
FDFS_CLIENT_CONF="./utils/fdfs/client.conf"

# 设置fdfs存储服务器上nginx的IP和端口号
FDFS_URL="http://192.168.12.232:8888/"
