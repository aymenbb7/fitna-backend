from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superadmin if it does not already exist'

    def handle(self, *args, **options):
        User = get_user_model()
        email = 'superadmin@fitna.dz'
        username = 'superadmin'
        password = 'Admin1234'
        full_name = 'Super Admin'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superadmin with email {email} already exists.'))
            u = User.objects.get(email=email)
            if not u.username:
                u.username = username
                u.save()
                self.stdout.write(self.style.SUCCESS(f'Updated username to {username} for existing superadmin.'))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                full_name=full_name
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superadmin {username} ({email}).'))
