import os
import django
import sys

sys.path.append(r'C:\Users\Amatek\Desktop\Fitna\fitna-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitna_backend.settings.base')
django.setup()

from modules.models import Module, Section, Lesson

module = Module.objects.get(slug='سوروبان')

section, created = Section.objects.get_or_create(
    module=module,
    title='Test Section E2E',
    defaults={'order': 1}
)

lesson, created = Lesson.objects.get_or_create(
    section=section,
    title='Test Lesson E2E',
    defaults={'order': 1}
)

print(f"Ensured Section '{section.title}' and Lesson '{lesson.title}' exist.")
