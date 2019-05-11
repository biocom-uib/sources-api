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
DATABASES = {
    'psql': ['computed', 'isobase', 'dip', 'intact', 'biogrid', 'mips', 'stringdb', 'stringdb_virus'],
    'mysql': ['geneontology']
}

computed = {
    'db': 'sources',
    'user':'sources',
    'pass':'sources',
    'host':'computed',
    'port':5432,
    'max_pool_conn': 50,
}

isobase =  {
    'db':'isobase',
    'user':'isobase',
    'pass':'isobase',
    'host':'isobase',
    'port': 5432,
    'max_pool_conn': 50,
}

dip =  {
    'db':'dip',
    'user':'dip',
    'pass':'dip',
    'host':'dip',
    'port': 5432,
    'max_pool_conn': 50,
}

intact =  {
    'db':'intact',
    'user':'intact',
    'pass':'intact',
    'host':'intact',
    'port': 5432,
    'max_pool_conn': 50,
}

biogrid =  {
    'db':'biogrid',
    'user':'biogrid',
    'pass':'biogrid',
    'host':'biogrid',
    'port': 5432,
    'max_pool_conn': 50,
}

mips =  {
    'db':'mips',
    'user':'mips',
    'pass':'mips',
    'host':'mips',
    'port': 5432,
    'max_pool_conn': 50,
}

stringdb =  {
    'db':'stringdb',
    'user':'stringdb',
    'pass':'stringdb',
    'host':'stringdb',
    'port': 5432,
    'max_pool_conn': 50,
}

stringdb_virus =  {
    'db':'stringdb_virus',
    'user':'stringdb_virus',
    'pass':'stringdb_virus',
    'host':'stringdb_virus',
    'port': 5432,
    'max_pool_conn': 50,
}

geneontology =  {
    'db':'geneontology',
    'user':'geneontology',
    'pass':'geneontology',
    'host':'geneontology',
    'port': 3306,
    'max_pool_conn': 50,
}


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
