import os
import django
import sys

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from modules.models import Module, Enrollment, Payment

User = get_user_model()
client = APIClient()

print("Starting Backend Verification...")

# 1. Check Super Admin
super_admin = User.objects.filter(role='SUPER_ADMIN').first()
if not super_admin:
    print("Creating dummy super admin...")
    super_admin = User.objects.create_user(email='admin@test.com', password='password', role='SUPER_ADMIN')

client.force_authenticate(user=super_admin)

# Verify Dashboard Stats
res = client.get('/api/v1/admin/stats/')
print(f"Dashboard stats: {res.status_code}")

res = client.get('/api/v1/admin/modules/dashboard-stats/')
print(f"Dashboard module stats: {res.status_code}")

# Verify Users
res = client.get('/api/v1/admin/users/')
print(f"Get all users: {res.status_code}")

# Verify Modules
res = client.get('/api/v1/admin/modules/')
print(f"Get all modules: {res.status_code}")

# Verify Revenue Stats
res = client.get('/api/v1/admin/revenue/stats/')
print(f"Revenue stats: {res.status_code}")

# Verify create student workflow
print("Testing Create Student with Payment...")
res = client.post('/api/v1/admin/students/create/', {
    'email': 'student_verify@test.com',
    'password': 'password123',
    'full_name': 'Test Student',
    'modules': [],
    'payments': []
}, format='json')
print(f"Create student: {res.status_code}")
if res.status_code == 200 or res.status_code == 201:
    print("Student created successfully.")

student = User.objects.filter(email='student_verify@test.com').first()

if student:
    # Test Module Stats Detail (if module exists)
    mod = Module.objects.first()
    if mod:
        res = client.get(f'/api/v1/admin/modules/{mod.slug}/stats/')
        print(f"Module stats detail: {res.status_code}")

    # Test Student payments
    res = client.get(f'/api/v1/admin/students/{student.id}/payments/')
    print(f"Student payments: {res.status_code}")
    
    # Delete student
    student.delete()

print("Verification check completed.")
