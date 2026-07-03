import os
import sys
import json
import django
from django.core.files.uploadedfile import SimpleUploadedFile
import responses
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from rest_framework.test import APIClient
from users.models import CustomUser
import core.views

client = APIClient()

super_admin = CustomUser.objects.filter(role='SUPER_ADMIN').first()
if not super_admin:
    super_admin = CustomUser.objects.create_user(email="testadmin@fitna.dz", password="pw", role="SUPER_ADMIN")

client.force_authenticate(user=super_admin)

# Mocking the Cloudinary API request inside our test script
@responses.activate
def test_upload():
    os.environ['CLOUDINARY_CLOUD_NAME'] = 'testcloudname'
    
    responses.add(
        responses.POST,
        'https://api.cloudinary.com/v1_1/testcloudname/auto/upload',
        json={
            "secure_url": "https://res.cloudinary.com/testcloudname/image/upload/v1234567/sample.jpg",
            "public_id": "sample"
        },
        status=200
    )

    dummy_file = SimpleUploadedFile("real_image.jpg", b"fake_image_content", content_type="image/jpeg")
    res_upload = client.post('/api/v1/upload/', {'file': dummy_file}, format='multipart')
    
    print("--- CLOUDINARY UPLOAD ENDPOINT RESPONSE ---")
    print(json.dumps(res_upload.json(), indent=2))
    
    if len(responses.calls) > 0:
        print("\n--- ACTUAL CLOUDINARY HTTP REQUEST SENT BY BACKEND ---")
        print("URL:", responses.calls[0].request.url)
        print("Body contains upload_preset=fitna_uploads:", b'upload_preset' in responses.calls[0].request.body and b'fitna_uploads' in responses.calls[0].request.body)

test_upload()

from quizzes.models import Quiz
from modules.models import Module

quran = Module.objects.first()
new_quiz = Quiz.objects.create(module=quran, title="New Quiz Defaults Test")

print("\n--- DEFAULT PASSING SCORE VERIFICATION ---")
print("Quiz passing_score in DB:", new_quiz.passing_score)

