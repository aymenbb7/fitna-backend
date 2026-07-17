
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()
from django.conf import settings
print('\n======================================')
print('DB ENGINE:', settings.DATABASES['default']['ENGINE'])
print('DB NAME:', settings.DATABASES['default'].get('NAME', 'N/A'))
print('DB HOST:', settings.DATABASES['default'].get('HOST', 'N/A'))
print('DB USER:', settings.DATABASES['default'].get('USER', 'N/A'))
print('======================================\n')

