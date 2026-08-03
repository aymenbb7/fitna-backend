import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings')
django.setup()

from modules.models import Module
from quizzes.models import Quiz
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.test import APIClient

client = APIClient()

module = Module.objects.first()
quiz = Quiz.objects.filter(module=module).first()

if not quiz:
    print("No quiz found")
    exit()

admin = User.objects.filter(role='SUPER_ADMIN').first()
client.force_authenticate(user=admin)

print(f"Creating question for quiz {quiz.id}...")
res = client.post(f'/api/v1/modules/{module.slug}/quizzes/{quiz.id}/questions/', {
    "text": "Test Question",
    "question_type": "MCQ",
    "points": 1,
    "explanation": "",
    "display_order": 0
}, format='json')

print("Status:", res.status_code)
print("Data:", res.data)

if res.status_code == 201:
    q_id = res.data['id']
    print("Creating choice...")
    c_res = client.post(f'/api/v1/modules/{module.slug}/quizzes/{quiz.id}/questions/{q_id}/choices/', {
        "text": "Choice 1",
        "is_correct": True,
        "display_order": 0
    }, format='json')
    print("Choice Status:", c_res.status_code)
    print("Choice Data:", c_res.data)
