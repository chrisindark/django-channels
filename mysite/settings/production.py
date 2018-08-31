from mysite.settings.base import *

SECRET_KEY = get_env_var('SECRET_KEY', 'secret')

ALLOWED_HOSTS = ()

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
            'level': 'DEBUG',  # message level to be written to console
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

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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
