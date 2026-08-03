import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import Notification

User = get_user_model()
superadmin = User.objects.filter(role='SUPER_ADMIN').first()
student = User.objects.filter(role='STUDENT').first()

if not student:
    student = User.objects.create_user(username='teststud', email='teststud@test.com', password='test', role='STUDENT')

c = APIClient()
c.force_authenticate(user=superadmin)

res = c.post('/api/v1/admin/notifications/broadcast/', {
    'title': 'Test Broadcast',
    'message': 'This is a test broadcast.',
    'target_type': 'ALL_STUDENTS',
    'target_ids': [],
    'send_email': False
}, format='json')

print("Broadcast Result:", res.status_code, getattr(res, 'data', ''))
print("Notifications for student:", Notification.objects.filter(recipient=student).count())

c.force_authenticate(user=student)
res2 = c.get('/api/v1/auth/notifications/')
print("Student Fetch Notifications Result:", res2.status_code, getattr(res2, 'data', ''))
