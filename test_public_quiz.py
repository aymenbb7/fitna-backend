import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings')
django.setup()

from modules.models import Module
from content.models import Lesson, Section
from quizzes.models import Quiz, Question, AnswerChoice
from rest_framework.test import APIClient

client = APIClient()

# Ensure we have a trial quiz
module = Module.objects.first()
if module:
    section, _ = Section.objects.get_or_create(module=module, title="Test Section", display_order=1)
    lesson, _ = Lesson.objects.get_or_create(section=section, title="Trial Lesson", is_active=True, is_preview=True)
    quiz, _ = Quiz.objects.get_or_create(module=module, lesson=lesson, title="Trial Quiz", is_active=True)
    
    if not quiz.questions.exists():
        q = Question.objects.create(quiz=quiz, text="Test Q", question_type="MCQ", points=10)
        c1 = AnswerChoice.objects.create(question=q, text="A", is_correct=True)
        c2 = AnswerChoice.objects.create(question=q, text="B", is_correct=False)
        
    print(f"Testing public start for Quiz {quiz.id} in Module {module.slug}...")
    res1 = client.get(f'/api/v1/modules/{module.slug}/quizzes/{quiz.id}/public_start/')
    print("Start Status:", res1.status_code)
    if res1.status_code == 200:
        print("Start Data:", res1.data)
        
        q_id = res1.data['quiz']['questions'][0]['id']
        c_id = res1.data['quiz']['questions'][0]['choices'][0]['id']
        
        print("\nTesting public submit...")
        res2 = client.post(f'/api/v1/modules/{module.slug}/quizzes/{quiz.id}/public_submit/', {
            "answers": [
                {
                    "question_id": q_id,
                    "choice_ids": [c_id]
                }
            ]
        }, format='json')
        print("Submit Status:", res2.status_code)
        print("Submit Data:", res2.data)
    else:
        print("Failed to start:", res1.data)
