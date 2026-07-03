from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Module, ModuleSettings

@receiver(post_save, sender=Module)
def create_module_settings(sender, instance, created, **kwargs):
    if created:
        ModuleSettings.objects.create(module=instance)
