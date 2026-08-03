import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from core.models import Module, User

try:
    admin = User.objects.filter(role='MODULE_ADMIN').first()
    Module.objects.create(name='Test', slug='test2', admin=admin)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
