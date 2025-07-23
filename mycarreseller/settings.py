# mycarreseller/settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here' # Altere esta chave em produção!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cars.apps.CarsConfig',  # Referência correta à classe AppConfig do seu aplicativo 'cars'
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

ROOT_URLCONF = 'mycarreseller.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Adiciona o diretório de templates global na raiz do projeto
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mycarreseller.context_processors.global_contact_info', # Adicione este context processor
            ],
        },
    },
]

WSGI_APPLICATION = 'mycarreseller.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br' # Altere para português do Brasil

TIME_ZONE = 'America/Sao_Paulo' # Altere para o fuso horário do Brasil

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Aponta para a pasta 'static' na raiz do projeto
]

# Media files (for user-uploaded content like car images)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Aponta para a pasta 'media' na raiz do projeto

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações de e-mail (para o formulário de contato)
# Para desenvolvimento, use o console backend para ver os e-mails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com' # Altere para o seu e-mail de remetente
SERVER_EMAIL = 'webmaster@yourdomain.com' # E-mail para erros do servidor

# INFORMAÇÕES DE CONTATO GLOBAIS (PARA O TOPBAR E RODAPÉ)
GLOBAL_CONTACT_INFO = {
    'address': 'Av. Fernando Corrêa da Costa, 400, Cuiabá - MT',
    'phone': '+55 (65) 1234-5678',
    'email': 'contato@cental.com.br',
    'facebook_url': 'https://www.facebook.com/seuperfil',
    'twitter_url': 'https://twitter.com/seuperfil',
    'instagram_url': 'https://www.instagram.com/seuperfil',
    'linkedin_url': 'https://www.linkedin.com/in/seuperfil',
}

# URL para redirecionar após o login bem-sucedido
# O usuário será redirecionado para o painel de gestão centralizado
LOGIN_REDIRECT_URL = '/dashboard/' # <--- ALTERADO para o novo painel central

# URL para redirecionar se o usuário não estiver logado e tentar acessar uma página protegida
# Por padrão, é /accounts/login/. Já está configurado no urls.py.
# LOGIN_URL = '/accounts/login/'

