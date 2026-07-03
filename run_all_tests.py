import os
import sys
import json
import django
from django.core.files.uploadedfile import SimpleUploadedFile
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from modules.models import Module, Enrollment
from users.models import CustomUser, Notification
from quizzes.models import Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer
from content.models import Document
from rest_framework.test import APIClient

client = APIClient()

print("\n--- 1. MODULE COLORS ---")
modules = Module.objects.all().order_by('display_order')
for m in modules:
    print(f"{m.slug}={m.color_primary}")

print("\n--- 2. NOTIFICATIONS ---")
# Register a student
admin_user = CustomUser.objects.filter(role='MODULE_ADMIN').first()
if not admin_user:
    admin_user = CustomUser.objects.create_user(email="admin_quran@fitna.dz", password="pw", role="MODULE_ADMIN", full_name="Quran Admin")
quran_module = Module.objects.get(slug='quran')
quran_module.admin = admin_user
quran_module.save()

# Delete old test users
CustomUser.objects.filter(email__in=['student_test_notifs@fitna.dz', 'reject_me@fitna.dz', 's3@fitna.dz', 'age25@fitna.dz']).delete()

# Enable all module settings
settings = quran_module.settings
settings.show_sessions = True
settings.show_pdfs = True
settings.show_videos = True
settings.show_voice = True
settings.show_photos = True
settings.show_quizzes = True
settings.save()

Notification.objects.all().delete()

# Register new student
res = client.post('/api/v1/auth/register/', {
    'email': 'student_test_notifs@fitna.dz',
    'password': 'pw',
    'full_name': 'Test Notif Student',
    'module_slug': 'quran',
    'age': 16
}, format='json')
student_user = CustomUser.objects.get(email='student_test_notifs@fitna.dz')

# Check admin notification
notif = Notification.objects.filter(recipient=admin_user, notification_type='NEW_STUDENT').first()
print(f"Admin NEW_STUDENT notification: {notif.message if notif else 'NOT FOUND'}")

# Approve student
client.force_authenticate(user=admin_user)
res = client.post(f'/api/v1/modules/quran/students/{student_user.id}/approve/')
notif = Notification.objects.filter(recipient=student_user, notification_type='STUDENT_APPROVED').first()
print(f"Student STUDENT_APPROVED notification: {notif.message if notif else 'NOT FOUND'}")

# Reject different student
student2 = CustomUser.objects.create_user(email="reject_me@fitna.dz", password="pw", full_name="Reject Me")
Enrollment.objects.create(student=student2, module=quran_module)
history_module = Module.objects.get(slug='history')
Enrollment.objects.create(student=student2, module=history_module)
res = client.post(f'/api/v1/modules/quran/students/{student2.id}/reject/')
notif = Notification.objects.filter(recipient=student2, notification_type='STUDENT_REJECTED').first()
print(f"Student STUDENT_REJECTED notification: {notif.message if notif else 'NOT FOUND'}")

# Create new Quiz
res = client.post('/api/v1/modules/quran/quizzes/', {
    'title': 'Test Quiz Notif',
    'is_active': True,
    'passing_score': 50
}, format='json')
notif = Notification.objects.filter(recipient=student_user, notification_type='NEW_QUIZ').first()
print(f"Student NEW_QUIZ notification: {notif.message if notif else 'NOT FOUND'}")

# Create new Content
res = client.post('/api/v1/modules/quran/documents/', {
    'title': 'Test Doc Notif',
    'file_url': 'http://test.com/doc.pdf',
    'doc_type': 'PDF',
    'is_active': True
}, format='json')
notif = Notification.objects.filter(recipient=student_user, notification_type='NEW_CONTENT').first()
print(f"Student NEW_CONTENT notification: {notif.message if notif else 'NOT FOUND'}")

print("\n--- 3. /api/v1/auth/me/ RESPONSE ---")
student_user.refresh_from_db()
client.force_authenticate(user=student_user)
res = client.get('/api/v1/auth/me/')
print(json.dumps(res.json(), indent=2))

print("\n--- 4. QUIZ END-TO-END FLOW ---")
client.force_authenticate(user=admin_user)
quiz = Quiz.objects.create(module=quran_module, title="End-to-End Quiz", is_active=True, passing_score=50)
q1 = Question.objects.create(quiz=quiz, text="What is 1+1?", points=10, question_type='MCQ')
AnswerChoice.objects.create(question=q1, text="1", is_correct=False)
q1_c2 = AnswerChoice.objects.create(question=q1, text="2", is_correct=True)

q2 = Question.objects.create(quiz=quiz, text="What is 2+2?", points=10, question_type='MCQ')
q2_c1 = AnswerChoice.objects.create(question=q2, text="4", is_correct=True)
AnswerChoice.objects.create(question=q2, text="5", is_correct=False)

client.force_authenticate(user=student_user)
res_start = client.post(f'/api/v1/modules/quran/quizzes/{quiz.id}/start/')
attempt_id = res_start.json()['attempt_id']

q2_wrong_choice = q2.choices.filter(is_correct=False).first()

res_submit = client.post(f'/api/v1/modules/quran/quizzes/{quiz.id}/submit/', {
    "attempt_id": attempt_id,
    "answers": [
        {"question_id": q1.id, "choice_ids": [q1_c2.id]},
        {"question_id": q2.id, "choice_ids": [q2_wrong_choice.id]}
    ]
}, format='json')
print(json.dumps(res_submit.json(), indent=2))

print("\n--- 5. QUIZ RESULTS ADMIN VIEW ---")
student3 = CustomUser.objects.create_user(email="s3@fitna.dz", password="pw", full_name="Student 3", is_approved=True)
Enrollment.objects.create(student=student3, module=quran_module)
client.force_authenticate(user=student3)
res_start3 = client.post(f'/api/v1/modules/quran/quizzes/{quiz.id}/start/')
attempt_id3 = res_start3.json()['attempt_id']
client.post(f'/api/v1/modules/quran/quizzes/{quiz.id}/submit/', {
    "attempt_id": attempt_id3,
    "answers": [
        {"question_id": q1.id, "choice_ids": [q1_c2.id]},
        {"question_id": q2.id, "choice_ids": [q2_c1.id]}
    ]
}, format='json')

client.force_authenticate(user=admin_user)
res_results = client.get(f'/api/v1/modules/quran/quizzes/{quiz.id}/results/')
print(json.dumps(res_results.json(), indent=2))

print("\n--- 6. ANALYTICS ---")
res_analytics = client.get('/api/v1/modules/quran/analytics/')
print(json.dumps(res_analytics.json(), indent=2))

print("\n--- 7. CLOUDINARY UPLOAD ---")
super_admin = CustomUser.objects.filter(role='SUPER_ADMIN').first()
client.force_authenticate(user=super_admin)
dummy_file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
res_upload = client.post('/api/v1/upload/', {'file': dummy_file}, format='multipart')
print(json.dumps(res_upload.json(), indent=2))

print("\n--- 8. PERMISSIONS (STUDENT ON ADMIN ENDPOINT) ---")
client.force_authenticate(user=student_user)
res_perm = client.get('/api/v1/modules/quran/analytics/')
print("Status Code:", res_perm.status_code)

print("\n--- 9. AGE VALIDATION ---")
client.logout()
res_age = client.post('/api/v1/auth/register/', {
    'email': 'age25@fitna.dz',
    'password': 'pw',
    'full_name': 'Old Guy',
    'age': 25,
    'module_slug': 'quran'
}, format='json')
print("Status Code:", res_age.status_code)
print("Response:", json.dumps(res_age.json(), indent=2))

print("\n--- 10. MODULE NOTE VISIBILITY ---")
client.force_authenticate(user=student_user)
student_user.module_note = "Private Note!"
student_user.save()
res_me = client.get('/api/v1/auth/me/')
print("module_note in /me/?", 'module_note' in res_me.json())
