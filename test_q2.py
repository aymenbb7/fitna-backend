from modules.models import Module
from quizzes.models import Quiz
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.test import APIClient

client = APIClient()
module = Module.objects.first()
quiz = Quiz.objects.filter(module=module).first()

admin = None
if hasattr(module, 'admin_profile'):
    admin = module.admin_profile.user

if not admin:
    print("No module admin found")
else:
    client.force_authenticate(user=admin)
    print(f"Testing as {admin.email}")
    res = client.post(f'/api/v1/modules/{module.slug}/quizzes/{quiz.id}/questions/', {
        'text': 'Test', 'question_type': 'MCQ', 'points': 1, 'display_order': 0
    }, format='json')
    print("Status:", res.status_code)
    if res.status_code == 201:
        q_id = res.data['id']
        c_res = client.post(f'/api/v1/modules/{module.slug}/quizzes/{quiz.id}/questions/{q_id}/choices/', {
            'text': 'Choice 1', 'is_correct': True, 'display_order': 0
        }, format='json')
        print("Choice Status:", c_res.status_code)
