"""
Base settings to build other settings files upon.
"""
from pathlib import Path

import environs

from api.logging_filters import CorrelationIdFilter


# (api/config/base.py - 2 = api/)
ROOT_DIR = Path(__file__).parent.parent

env = environs.Env()

READ_DOT_ENV_FILE = env.bool('READ_DOT_ENV_FILE', default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR/'.env'), False)

# GENERAL
# -----------------------------------------------------------------------------
DEBUG = env.bool('DEBUG', default=False)


# DATABASES
# -----------------------------------------------------------------------------
MONGODB_DSN = env('MONGODB_DSN',
                  default='mongodb://airamleib:airamleib@mongo/airam_leib')


# LOGGING
# -----------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': env('LOGGING_LEVEL', 'INFO'),
        'handlers': ['console'],
    },
    'formatters': {
        'default': {
            'format': "%(asctime)s %(levelname)s %(name)s %(correlationid)s | %(message)s",
        },
    },
    'filters': {
        'correlationid': {
            '()': CorrelationIdFilter,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['correlationid'],
        },
    },
    'loggers': {
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
ACCESS_LOG_FORMAT = env('ACCESS_LOG_FORMAT', '"%r" %s %b %Tf')
TRACING_ENABLED = env.bool('TRACING_ENABLED', False)
SENTRY_DSN = "https://1a2fa23db22a4ea9be27ca968bcc4419@sentry.io/1422329"
