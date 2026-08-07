from rest_framework import serializers
from .models import SiteSettings

class SiteSettingsSerializer(serializers.ModelSerializer):
    whatsapp_number = serializers.CharField(source='social_whatsapp', read_only=True)

    class Meta:
        model = SiteSettings
        fields = '__all__'
