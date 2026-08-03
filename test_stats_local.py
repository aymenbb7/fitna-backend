import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()
u = User.objects.get(username='admin')
c = APIClient()
c.force_authenticate(user=u)

print('Testing SuperAdminStatsView...')
res = c.get('/api/v1/admin/stats/')
print(res.status_code)
if res.status_code != 200:
    print(res.data)

print('\nTesting DashboardModuleStatsView...')
res2 = c.get('/api/v1/admin/modules/dashboard-stats/')
print(res2.status_code)
if res2.status_code != 200:
    print(res2.data)
