import os
import sys

from .settings import *  # noqa
from .settings import BASE_DIR

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
DEBUG = False

# WhiteNoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configure Postgres database based on connection string of the libpq Keyword/Value form
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': conn_str_params['dbname'],
        'HOST': conn_str_params['host'],
        'USER': conn_str_params['user'],
        'PASSWORD': conn_str_params['password'],
    }
}

# LOGGING["root"]["level"] = 'INFO'

sampler = 'opencensus.trace.samplers.ProbabilitySampler(rate=1.0)'
OPENCENSUS = {
    'TRACE': {
        'SAMPLER': sampler,
        'EXPORTER': 'opencensus.ext.azure.trace_exporter.AzureExporter(connection_string="InstrumentationKey=bba4e20f-fd75-471e-9ad2-68419df0b1cc;IngestionEndpoint=https://germanywestcentral-1.in.applicationinsights.azure.com/;LiveEndpoint=https://germanywestcentral.livediagnostics.monitor.azure.com/")',
    }
}

LOGGING = {
    "handlers": {
        "azure": {
            "level": "DEBUG",
            "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
            "connection_string": "<appinsights-connection-string>",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
      },
    "loggers": {
        "logger": {"handlers": ["azure", "console"]},
    },
}