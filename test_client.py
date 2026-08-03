import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
c = Client()
user, _ = User.objects.get_or_create(username='su2', email='su2@test.com', role='SUPER_ADMIN')
user.set_password('123')
user.is_superuser = True
user.save()

res = c.post('/api/v1/auth/login/', {'username': 'su2', 'password': '123'}, content_type='application/json')
token = res.json().get('access')

res = c.post('/api/v1/admin/modules/create/', {'name': 'Test3', 'slug': 'test3', 'price': ""}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {token}')
print("Status:", res.status_code)
print("Content:", res.content.decode())
