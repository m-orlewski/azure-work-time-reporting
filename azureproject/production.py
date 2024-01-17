import os

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
    'opencensus.ext.django.middleware.OpencensusMiddleware',
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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(processName)s - %(name)s\n%(message)s',
        },
    },
    'handlers': {
         'azure': {
            'level': "DEBUG",
            'class': 'opencensus.ext.azure.log_exporter.AzureLogHandler',
            'instrumentation_key':'facca527-f17a-49e4-87fd-12bcff3c5b26', # entered explicitly just for tests
            "formatter": "default",
          },
        'console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
            "formatter": "default",
        },
    },
    'loggers': {
        'polls': {
            'level':'DEBUG',
            'handlers': ['azure', 'console'],
            },
    },
}

def shorten_url(envelope):
    if 25 < len(envelope.data.baseData.url):
        envelope.data.baseData["url"] = envelope.data.baseData.url[:25]+"..." 
    return True

from opencensus.ext.azure.trace_exporter import AzureExporter
exporter = AzureExporter(service_name='azureproject')
exporter.add_telemetry_processor(shorten_url)

OPENCENSUS = {
    'TRACE': {
        'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=1)',
        'EXPORTER': exporter
    }
}