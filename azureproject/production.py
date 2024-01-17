import os

from .settings import *  # noqa
from .settings import BASE_DIR

from opencensus.trace import config_integration

config_integration.trace_integrations(['requests','logging','postgresql'])


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
    'opencensus.ext.django.middleware.OpencensusMiddleware',
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

OPENCENSUS = {
    'TRACE': {
        'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=1)',
        'EXPORTER': '''opencensus.ext.azure.trace_exporter.AzureExporter(
            connection_string="InstrumentationKey=<your-ikey-here>"
        )''',
    }
}

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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s | %(levelname)s | %(message)s"
        },
        "azure_verbose": {
            "format": "%(asctime)s |  %(name)s | %(levelname)s | [%(funcName)s:%(filename)s:%(lineno)d] |"
        },

    },
    "handlers": {
        "stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "log_to_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "logs", "dev.logs") # same loc as blogproject
        },
         "log_to_azure_ai": {
            "level": "DEBUG",
            "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
            "connection_string": os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
            "formatter": "verbose",
        },

    },
    "loggers": {
        'django': {
            'handlers': ['stdout', 'log_to_file','log_to_azure_ai'],
        },
    }
}