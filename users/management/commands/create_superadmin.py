from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superadmin if it does not already exist'

    def handle(self, *args, **options):
        User = get_user_model()
        email = 'superadmin@fitna.dz'
        password = 'Admin1234'
        full_name = 'Super Admin'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superadmin with email {email} already exists.'))
        else:
            User.objects.create_superuser(
                email=email,
                password=password,
                full_name=full_name
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superadmin {email}.'))
