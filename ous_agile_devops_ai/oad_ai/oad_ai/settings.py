import os
from pathlib import Path
from decouple import config
from datetime import timedelta
import saml2
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED
import saml2.xmldsig
import saml2.saml
from cryptography.fernet import Fernet
from urllib.parse import urljoin

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Define the base URL
#BASE_URL = config('BASE_URL', default='http://localhost:8001')
BASE_URL = config('BASE_URL', default='http://oad-ai.abbvienet.com:8001')

# Media settings with improved structure
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Define specific media subdirectories
MEDIA_SUBDIRS = {
    'AUTO_UPLOAD': 'auto_upload',
    'PREVIEWS': 'previews',
    'MANUAL_CHECK': 'manual_check'
}

# Create full paths for media subdirectories
AUTO_UPLOAD_DIR = os.path.join(MEDIA_ROOT, MEDIA_SUBDIRS['AUTO_UPLOAD'])
PREVIEW_DIR = os.path.join(MEDIA_ROOT, MEDIA_SUBDIRS['PREVIEWS'])
MANUAL_CHECK_DIR = os.path.join(MEDIA_ROOT, MEDIA_SUBDIRS['MANUAL_CHECK'])

# Preview URL settings
PREVIEW_BASE_URL = BASE_URL
PREVIEW_URL_PATH = urljoin(MEDIA_URL, f"{MEDIA_SUBDIRS['PREVIEWS']}/")

# Ensure all required directories exist
for directory in [MEDIA_ROOT, AUTO_UPLOAD_DIR, PREVIEW_DIR, MANUAL_CHECK_DIR]:
    os.makedirs(directory, exist_ok=True)

ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.72.19.8', 'oad-ai.abbvienet.com']

ENCRYPTION_KEY = config('ENCRYPTION_KEY')
ENCRYPTED_API_KEY = config('ENCRYPTED_API_KEY')
AUTH_TOKEN = config('AUTH_TOKEN')
fernet = Fernet(ENCRYPTION_KEY.encode())
ILIAD_API_KEY = fernet.decrypt(ENCRYPTED_API_KEY.encode()).decode()

# File upload settings
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.txt', '.md', '.png', '.jpg', '.jpeg']
MAX_UPLOAD_SIZE = 10485760  # 10MB in bytes

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
    'csp',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangosaml2.middleware.SamlSessionMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'oad_ai.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.template.context_processors.media',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'oad_ai.wsgi.application'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# URL settings based on environment
if DEBUG:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
else:
    STATIC_URL = f'{BASE_URL}/static/'
    MEDIA_URL = f'{BASE_URL}/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    f"{BASE_URL.replace(':8001', ':3000')}",
    f"{BASE_URL.replace(':8001', ':3001')}",
    "http://10.72.19.8",
    "http://oad-ai.abbvienet.com:3001",
    BASE_URL,
]

CSRF_TRUSTED_ORIGINS = [
    f"{BASE_URL.replace(':8001', ':3000')}",
    f"{BASE_URL.replace(':8001', ':3001')}",
    "http://10.72.19.8",
    "http://oad-ai.abbvienet.com:3001",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'djangosaml2.backends.Saml2Backend',
    ),
}

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

ASGI_APPLICATION = 'oad_ai.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {"hosts": [('127.0.0.1', 6379)]},
    },
}

# SAML2 Configuration
SAML_CONFIG = {
    'xmlsec_binary': r'C:\path\to\xmlsec.exe',
    'entityid': f'{BASE_URL}/saml2/metadata/',
    'allow_unknown_attributes': True,
    'service': {
        'sp': {
            'name': 'Test SP',
            'endpoints': {
                'assertion_consumer_service': [
                    (f'{BASE_URL}/saml2/acs/', saml2.BINDING_HTTP_POST),
                ],
                'single_logout_service': [
                    (f'{BASE_URL}/saml2/slo/', saml2.BINDING_HTTP_REDIRECT),
                ],
            },
            'allow_unsolicited': True,
            'authn_requests_signed': False,
            'logout_requests_signed': True,
            'want_assertions_signed': True,
            'want_response_signed': False,
            'name_id_format': saml2.saml.NAMEID_FORMAT_UNSPECIFIED,
            'force_authn': False,
            'name_id_policy_format': saml2.saml.NAMEID_FORMAT_UNSPECIFIED,
            'sign_alg': saml2.xmldsig.SIG_RSA_SHA256,
            'digest_alg': saml2.xmldsig.DIGEST_SHA256,
            'required_attributes': ['email'],
            'optional_attributes': ['firstName', 'lastName'],
        },
    },
    'metadata': {
        'local': [
            os.path.join(BASE_DIR, 'path/to/sp-metadata.xml'),
            os.path.join(BASE_DIR, 'path/to/idp_metadata.xml')
        ]
    },
    'key_file': os.path.join(BASE_DIR, 'path/to/new-idp-key.pem'),
    'cert_file': os.path.join(BASE_DIR, 'path/to/new-idp-cert.pem'),
    'encryption_keypairs': [{
        'key_file': os.path.join(BASE_DIR, 'path/to/new-idp-key.pem'),
        'cert_file': os.path.join(BASE_DIR, 'path/to/new-idp-cert.pem'),
    }],
    'valid_for': 24,
    'debug': True,
}

SAML_ATTRIBUTE_MAPPING = {
    'uid': ('username',),
    'mail': ('email',),
    'givenname': ['first_name'],
    'sn': ('last_name',)
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SAML_METADATA_PATH = os.path.join(BASE_DIR, 'SAML_METADATA_PATH')

LOGIN_URL = f'{BASE_URL.replace(":8001", ":3001")}/login'
LOGIN_REDIRECT_URL = BASE_URL.replace(":8001", ":3001")
LOGOUT_REDIRECT_URL = BASE_URL

# Logging Configuration
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
            'level': 'DEBUG',
        },
        'djangosaml2': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'chatbot1': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-eval'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "'unsafe-inline'", "https:", "data:", f"{BASE_URL}")
CSP_FONT_SRC = ("'self'",)
CSP_MEDIA_SRC = ("'self'", f"{BASE_URL}")

# SAML2 Additional Settings
SAML_CREATE_UNKNOWN_USERS = True
SAML_IGNORE_AUTHENTICATED_USERS = False
SAML2_AUTH = {
    'BINDING': 'HTTP-REDIRECT'
}