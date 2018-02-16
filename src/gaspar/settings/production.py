from .base import *
import os
import raven

DEBUG = False
INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': 'https://4b314bfca37d42a2abc9290f37d4db97:84378df2da8a4af998e1c9418faf1b06@sentry.io/184724',
}
