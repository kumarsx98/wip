import os
from pathlib import Path
from decouple import config, Csv, AutoConfig
from cryptography.fernet import Fernet
from datetime import timedelta
import saml2
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Determine which environment file to use and set configuration
env_file = '.envserver' if os.path.isfile(BASE_DIR / '.envserver') else '.env'
config = AutoConfig(search_path=BASE_DIR)

# Media files configuration
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
PREVIEW_BASE_URL = MEDIA_URL

# Load sensitive information from environment variables
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
ENCRYPTION_KEY = config('ENCRYPTION_KEY')
ENCRYPTED_API_KEY = config('ENCRYPTED_API_KEY')
AUTH_TOKEN = config('AUTH_TOKEN')
ILIAD_URL = config('ILIAD_URL')
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=False, cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

# Decrypt API Key
fernet = Fernet(ENCRYPTION_KEY.encode())
ILIAD_API_KEY = fernet.decrypt(ENCRYPTED_API_KEY.encode()).decode()

# Custom Middleware for Request Timeout


# Installed apps and middleware
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbot1',
    'corsheaders',
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'djangosaml2',
    'csp'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangosaml2.middleware.SamlSessionMiddleware',
    'csp.middleware.CSPMiddleware',
    'oad_ai.middleware.XFrameOptionsMiddleware',  # Custom middleware for X-Frame-Options
    #'oad_ai.timeout_middleware.TimeoutMiddleware',  # Custom Timeout Middleware
]

# URL and template configuration
ROOT_URLCONF = 'oad_ai.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
WSGI_APPLICATION = 'oad_ai.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # Increase connection age in seconds (10 minutes)
    }
}

# Authentication and password validation
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

# Localization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_CREDENTIALS = CORS_ALLOW_CREDENTIALS
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'djangosaml2.backends.Saml2Backend',
    )
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Channels settings
ASGI_APPLICATION = 'oad_ai.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# SAML2 settings
AUTHENTICATION_BACKENDS = (
    'djangosaml2.backends.Saml2Backend',
    'django.contrib.auth.backends.ModelBackend',
)
SAML_CONFIG = {
    'xmlsec_binary': r'C:\Users\AMX1\Downloads\Repo\OAD_Auto\xmlsec\libxmlsec-1.2.18.win32\bin\xmlsec.exe',
    'entityid': 'http://localhost:8001/saml2/metadata/',
    'allow_unknown_attributes': True,
    'service': {
        'sp': {
            'name': 'Your SP Name',
            'endpoints': {
                'assertion_consumer_service': [
                    ('http://localhost:8001/saml2/acs/', saml2.BINDING_HTTP_REDIRECT),
                ],
                'single_logout_service': [
                    ('http://localhost:8001/saml2/slo/', saml2.BINDING_HTTP_REDIRECT),
                ],
            },
            'allow_unsolicited': True,
            'authn_requests_signed': False,
            'logout_requests_signed': True,
            'want_assertions_signed': True,
            'want_response_signed': False,
            'name_id_format': NAMEID_FORMAT_UNSPECIFIED,
            'force_authn': False,
            'name_id_policy_format': NAMEID_FORMAT_UNSPECIFIED,
            'sign_alg': saml2.xmldsig.SIG_RSA_SHA256,
            'digest_alg': saml2.xmldsig.DIGEST_SHA256,
            'required_attributes': ['email'],
            'optional_attributes': ['firstName', 'lastName'],
        },
    },
    'metadata': {
        'local': [os.path.join(BASE_DIR, 'idp_metadata.xml')],
    },
    'key_file': os.path.join(BASE_DIR, 'new-idp-key.pem'),
    'cert_file': os.path.join(BASE_DIR, 'new-idp-cert.pem'),
    'encryption_keypairs': [{
        'key_file': os.path.join(BASE_DIR, 'new-idp-key.pem'),
        'cert_file': os.path.join(BASE_DIR, 'new-idp-cert.pem'),
    }],
    'valid_for': 24,
    'debug': True,
}
SAML_ATTRIBUTE_MAPPING = {
    'email': ('email',),
    'firstName': ('first_name',),
    'lastName': ('last_name',),
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SAML_METADATA_PATH = os.path.join(BASE_DIR, 'sp_metadata.xml')

LOGIN_URL = '/saml2/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'djangosaml2': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:", "data:")

SAML_CREATE_UNKNOWN_USER = True
SAML_IGNORE_AUTHENTICATED_USERS = False
SAML2_AUTH = {'BINDING': 'HTTP-REDIRECT',}
