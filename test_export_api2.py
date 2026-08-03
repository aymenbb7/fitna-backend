from django.test import RequestFactory
from core.views import UsersExportView
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(role='SUPER_ADMIN').first()
if not admin_user:
    admin_user = User.objects.create(email='admin@test.com', role='SUPER_ADMIN')

factory = RequestFactory()
view = UsersExportView.as_view()

for fmt in ['csv', 'excel', 'pdf']:
    request = factory.get(f'/admin/users/export/?role=STUDENT&format={fmt}')
    request.user = admin_user
    try:
        response = view(request)
        print(f"Format: {fmt}, Status: {response.status_code}")
    except Exception as e:
        import traceback
        print(f"Format: {fmt} failed with exception:")
        traceback.print_exc()
