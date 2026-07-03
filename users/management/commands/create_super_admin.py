from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates the default super admin'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = "admin@fitna.dz"
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password="FitnaAdmin2025!",
                full_name="Super Admin"
            )
            self.stdout.write(self.style.SUCCESS('Super admin created'))
        else:
            self.stdout.write(self.style.WARNING('Already exists'))
