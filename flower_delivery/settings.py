import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка конфигурации из config.json
with open(os.path.join(BASE_DIR, 'config.json')) as config_file:
    config = json.load(config_file)

# Секретный ключ и настройки отладки
SECRET_KEY = config.get('secret_key', 'django-insecure-)m*(m4k=ee(*m8gpbmp2t-(6v)p%w4d%7@w2)@uj@5s3+4_b&(')
DEBUG = config.get('debug', False)

ALLOWED_HOSTS = config.get('allowed_hosts', ['fd.vivikey.tech'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'orders.apps.OrdersConfig',
    'rest_framework',
    'users',
    'fileviewer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flower_delivery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'flower_delivery.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',  # Уровень логирования
            'class': 'logging.StreamHandler',  # Класс, отвечающий за вывод в консоль
        },
    },
    'loggers': {
        'my_custom_logger': {
            'handlers': ['console'],  # Подключаем handler 'console' к нашему кастомному логгеру
            'level': 'DEBUG',  # Уровень логирования для кастомного логгера
            'propagate': False,  # Отключаем передачу сообщений другим логгерам
        },
    },
}


AIORGRAM_API_TOKEN = config['telegram_token']
WEBHOOK_URL = config['webhook_url']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Session management
SESSION_COOKIE_AGE = 1209600  # 2 недели
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Сессия сохраняется после закрытия браузера

# Redirect settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'  # URL для страницы логина

AUTH_USER_MODEL = 'users.CustomUser'
