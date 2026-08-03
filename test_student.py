import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from modules.models import Payment, Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()
student = User.objects.get(email='new_multi@test.com')

print("Enrollments:", Enrollment.objects.filter(student=student).count())
print("Payments:", Payment.objects.filter(student=student).count())
