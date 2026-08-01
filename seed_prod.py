import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.production')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from modules.models import Module

def run_seed():
    print("1. Creating Super Admin...")
    call_command('create_superadmin')
    
    print("\n2. Creating 9 Original Modules...")
    call_command('seed_modules')
    
    print("\n3. Creating Module Admin Accounts...")
    User = get_user_model()
    modules = Module.objects.all()
    created_count = 0
    
    for module in modules:
        email = f"admin_{module.slug}@fitna.dz"
        if not User.objects.filter(email=email).exists():
            User.objects.create_user(
                username=f"admin_{module.slug}",
                email=email,
                password="Admin1234",
                full_name=f"Admin {module.name}",
                role="MODULE_ADMIN",
                is_active=True,
                is_approved=True
            )
            print(f" - Created module admin for {module.name} ({email})")
            created_count += 1
        else:
            print(f" - Module admin for {module.name} already exists ({email})")
            
    print(f"\nCreated {created_count} module admins.")
    print("\nSeed process completed successfully.")

if __name__ == '__main__':
    run_seed()
