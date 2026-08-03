from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(role='SUPER_ADMIN').first()
if not admin_user:
    admin_user = User.objects.create(email='admin@test.com', role='SUPER_ADMIN')

client = Client()
client.force_login(admin_user)

for fmt in ['csv', 'excel', 'pdf']:
    response = client.get(f'/api/v1/admin/users/export/?role=STUDENT&format={fmt}')
    print(f"Format: {fmt}, Status: {response.status_code}")
    if response.status_code != 200:
        print("Response content:", response.content)
