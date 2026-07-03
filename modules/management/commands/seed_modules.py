from django.core.management.base import BaseCommand
from modules.models import Module

class Command(BaseCommand):
    help = 'Seeds the database with default modules'

    def handle(self, *args, **kwargs):
        modules = [
            {"name": "قسم التعليم القرآني", "slug": "quran", "background_theme": "QURAN", "icon": "🕌", "display_order": 1, "color_primary": "#1B5E20"},
            {"name": "قسم الذاكرة", "slug": "memory", "background_theme": "MEMORY", "icon": "🧠", "display_order": 2, "color_primary": "#1565C0"},
            {"name": "قسم السوروبان", "slug": "soroban", "background_theme": "SOROBAN", "icon": "🧮", "display_order": 3, "color_primary": "#E65100"},
            {"name": "قسم التدريب على حل الإشكال", "slug": "problem-solving", "background_theme": "PROBLEM_SOLVING", "icon": "🧩", "display_order": 4, "color_primary": "#6A1B9A"},
            {"name": "قسم العادات الصحية", "slug": "health", "background_theme": "HEALTH", "icon": "🌿", "display_order": 5, "color_primary": "#2E7D32"},
            {"name": "قسم التاريخ", "slug": "history", "background_theme": "HISTORY", "icon": "🏛️", "display_order": 6, "color_primary": "#BF360C"},
            {"name": "قسم اللغات", "slug": "languages", "background_theme": "LANGUAGES", "icon": "🗣️", "display_order": 7, "color_primary": "#00695C"},
            {"name": "قسم المواهب", "slug": "talents", "background_theme": "TALENTS", "icon": "⭐", "display_order": 8, "color_primary": "#F57F17"},
            {"name": "قسم المتابعة النفسية", "slug": "psychology", "background_theme": "PSYCHOLOGY", "icon": "🧘", "display_order": 9, "color_primary": "#4527A0"}
        ]

        for mod_data in modules:
            Module.objects.get_or_create(
                slug=mod_data["slug"],
                defaults=mod_data
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded modules'))
