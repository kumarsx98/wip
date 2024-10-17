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

BASE_DIR = Path(__file__).resolve().parent.parent

# Define the base URL
#BASE_URL = config('BASE_URL', default='http://localhost:8001')
BASE_URL = config('BASE_URL', default='http://oad-ai.abbvienet.com:8001')


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
PREVIEW_BASE_URL = MEDIA_URL

ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.72.19.8', 'oad-ai.abbvienet.com']

ENCRYPTION_KEY = config('ENCRYPTION_KEY')
ENCRYPTED_API_KEY = config('ENCRYPTED_API_KEY')
AUTH_TOKEN = config('AUTH_TOKEN')
fernet = Fernet(ENCRYPTION_KEY.encode())
ILIAD_API_KEY = fernet.decrypt(ENCRYPTED_API_KEY.encode()).decode()

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
    'DIRS': [],  # You can specify your template directories here if needed
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

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3',}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    f"{BASE_URL.replace('8001', '3000')}", # "http://localhost:3000"
    f"{BASE_URL.replace('8001', '3001')}", # "http://localhost:3001"
    "http://10.72.19.8",
    "http://oad-ai.abbvienet.com:3001",
]

CSRF_TRUSTED_ORIGINS = [
    f"{BASE_URL.replace('8001', '3000')}", # "http://localhost:3000"
    f"{BASE_URL.replace('8001', '3001')}", # "http://localhost:3001"
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

SAML_CONFIG = {
    'xmlsec_binary': r'C:\Users\AMX1\Downloads\Repo\5-Sep\xmlsec\libxmlsec-1.2.18.win32\bin\xmlsec.exe',
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
            os.path.join(BASE_DIR, r'C:\Users\AMX1\Downloads\Repo\5-Sep\ous_agile_devops_ai\oad_ai\sp-metadata.xml'),
            os.path.join(BASE_DIR, r'C:\Users\AMX1\Downloads\Repo\5-Sep\ous_agile_devops_ai\oad_ai\idp_metadata.xml')
        ]
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
    'uid': ('username',),
    'mail': ('email',),
    'givenname': ['first_name'],
    'sn': ('last_name',)
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SAML_METADATA_PATH = os.path.join(BASE_DIR, r'SAML_METADATA_PATH')

# Update these URLs to point to the new React component route
# Ensure the redirection URLs are correct
LOGIN_URL = f'{BASE_URL.replace("8001", "3001")}/login'
LOGIN_REDIRECT_URL = BASE_URL.replace("8001", "3001")  # Redirect to the main page after successful login
LOGOUT_REDIRECT_URL = BASE_URL
# Alternatively, if the home page is on the same URL as the BASE_URL
# LOGOUT_REDIRECT_URL = '/'

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
    }
}

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-eval'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "'unsafe-inline'", "https:")
CSP_FONT_SRC = ("'self'",)

SAML_CREATE_UNKNOWN_USERS = True
SAML_IGNORE_AUTHENTICATED_USERS = False
SAML2_AUTH = {
    'BINDING': 'HTTP-REDIRECT'
}
