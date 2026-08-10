"""
Management command: activate_all_media
=======================================
Finds all Document, Video, VoiceMessage, Photo, Session objects
where is_active=False and bulk-activates them.

This is a one-time data repair for items created before the
is_active fix in AddResourceModal.jsx and BaseContentViewSet.perform_create.

Usage:
    python manage.py activate_all_media [--dry-run]
"""
from django.core.management.base import BaseCommand
from content.models import Document, Video, VoiceMessage, Photo, Session


MODELS = [
    ('Video',        Video),
    ('Document',     Document),
    ('VoiceMessage', VoiceMessage),
    ('Photo',        Photo),
    ('Session',      Session),
]


class Command(BaseCommand):
    help = 'Activate all media items that were created with is_active=False (data repair command)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing anything',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        total_fixed = 0

        for name, Model in MODELS:
            inactive = Model.objects.filter(is_active=False)
            count = inactive.count()

            if count == 0:
                self.stdout.write(f'  OK       {name}: 0 inactive')
                continue

            items = list(inactive.values('id', 'title', 'lesson__section__module__slug'))
            for item in items:
                self.stdout.write(
                    f'  {"[DRY] " if dry_run else ""}FIXING {name} id={item["id"]} '
                    f'module={item["lesson__section__module__slug"]} '
                    f'title={item["title"]!r:.50}'
                )

            if not dry_run:
                updated = Model.objects.filter(is_active=False).update(is_active=True)
                self.stdout.write(self.style.SUCCESS(f'  FIXED {name}: activated {updated} items'))
                total_fixed += updated
            else:
                total_fixed += count

        if dry_run:
            self.stdout.write(self.style.WARNING(f'\n[DRY RUN] Would fix {total_fixed} items. Re-run without --dry-run to apply.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nTotal activated: {total_fixed} items'))
