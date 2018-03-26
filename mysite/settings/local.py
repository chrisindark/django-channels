from mysite.settings.base import *

# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var('SECRET_KEY', 'secret')

ALLOWED_HOSTS = (
    'localhost',
    '127.0.0.1',
    '172.16.9.234',
    '192.168.1.104',
    'protected-bastion-26995.herokuapp.com',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG', # message level to be written to console
            # logging handler that outputs log messages to terminal
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': {
            # this sets root level logger to log debug and higher level
            # logs to console. All other loggers inherit settings from
            # root level logger.
            'handlers': ['console'],
            'level': 'DEBUG',
            # this tells logger to send logging message
            # to its parent (will send if set to True)
            'propagate': False
        },
        'django.db': {
            # 'level': 'DEBUG'
            # django also has database level logging
        },
    },
}

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/accounts/logout/'
LOGOUT_REDIRECT_URL = '/'

INSTALLED_APPS += (
    'django_extensions',
)

MIDDLEWARE += ()

CORS_ORIGIN_WHITELIST = ()
CORS_ORIGIN_ALLOW_ALL = True

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Channel settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
        "ROUTING": "mysite.routing.channel_routing",
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# EMAIL SETTINGS
# EMAIL_USE_TLS = True
# EMAIL_HOST = ''
# EMAIL_PORT = 587
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': get_env_var('DB_NAME'),
    'USER': get_env_var('DB_USERNAME'),
    'PASSWORD': get_env_var('DB_PASSWORD'),
    'HOST': get_env_var('DB_HOST'),
    'PORT': get_env_var('DB_PORT'),
}
