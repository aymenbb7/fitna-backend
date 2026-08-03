from rest_framework import views, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.permissions import IsSuperAdmin
from .models import SiteSettings
from django.core.mail import send_mail
from django.conf import settings

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'smtp_host', 'smtp_port', 'smtp_username', 'smtp_use_tls', 
            
            # Branding
            'site_name', 'logo', 'logo_url', 'site_primary_color', 'site_secondary_color',
            
            'landing_hero_title', 'landing_hero_subtitle', 'landing_hero_button_text', 'landing_hero_button_url',
            'landing_hero_image',
            'landing_about_title', 'landing_about_text', 'landing_about_image',
            
            'landing_programs_json', 'landing_features_json', 'landing_stats_json', 
            'landing_testimonials_json', 'landing_faq_json',
            'landing_features_title', 'landing_features_subtitle', 'landing_stats_title',
            'landing_programs_title', 'landing_how_it_works_title', 'landing_testimonials_title',
            'landing_faq_title',
            
            'landing_cta_title', 'landing_cta_text', 'landing_cta_button_text', 'landing_cta_button_url',
            
            'contact_email', 'contact_phone', 'contact_address',
            
            'footer_text', 'footer_desc', 'social_facebook', 'social_instagram', 'social_tiktok', 'social_whatsapp'
        ]

class SiteSettingsView(views.APIView):
    permission_classes = (IsSuperAdmin,)
    
    def get(self, request):
        s = SiteSettings.get_settings()
        data = SiteSettingsSerializer(s, context={'request': request}).data
        data['smtp_password'] = "********" if s.smtp_password else ""
        return Response(data)
        
    def post(self, request):
        s = SiteSettings.get_settings()
        action = request.data.get("action", "update")
        
        if action == "test_email":
            email = request.data.get("email")
            if not email:
                return Response({"error": "Email is required"}, status=400)
            try:
                from django.core.mail.backends.smtp import EmailBackend
                backend = EmailBackend(
                    host=s.smtp_host,
                    port=s.smtp_port,
                    username=s.smtp_username,
                    password=s.smtp_password,
                    use_tls=s.smtp_use_tls,
                    fail_silently=False
                )
                
                send_mail(
                    "Test Email from Fitna",
                    "This is a test email to verify your SMTP settings.",
                    s.smtp_username or settings.DEFAULT_FROM_EMAIL,
                    [email],
                    connection=backend,
                    fail_silently=False
                )
                return Response({"message": "Test email sent successfully!"})
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        else:
            # Text/field updates
            text_fields = [
                'site_name', 'logo_url', 'site_primary_color', 'site_secondary_color',
                'landing_hero_title', 'landing_hero_subtitle', 'landing_hero_button_text', 'landing_hero_button_url',
                'landing_about_title', 'landing_about_text',
                'landing_programs_json', 'landing_features_json', 'landing_stats_json',
                'landing_testimonials_json', 'landing_faq_json',
                'landing_features_title', 'landing_features_subtitle', 'landing_stats_title',
                'landing_programs_title', 'landing_how_it_works_title', 'landing_testimonials_title',
                'landing_faq_title',
                'landing_cta_title', 'landing_cta_text', 'landing_cta_button_text', 'landing_cta_button_url',
                'contact_email', 'contact_phone', 'contact_address',
                'footer_text', 'footer_desc',
                'social_facebook', 'social_instagram', 'social_tiktok', 'social_whatsapp',
                'smtp_host', 'smtp_port', 'smtp_username', 'smtp_use_tls',
            ]
            for field in text_fields:
                if field in request.data:
                    setattr(s, field, request.data[field])
            
            # File uploads
            if 'logo' in request.FILES:
                s.logo = request.FILES['logo']
            if 'landing_hero_image' in request.FILES:
                s.landing_hero_image = request.FILES['landing_hero_image']
            if 'landing_about_image' in request.FILES:
                s.landing_about_image = request.FILES['landing_about_image']
                    
            # Handle password separately
            if 'smtp_password' in request.data and request.data['smtp_password'] and request.data['smtp_password'] != "********":
                s.smtp_password = request.data['smtp_password']
                
            s.save()
            return Response({"message": "Settings updated successfully"})

class PublicSiteSettingsView(views.APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        s = SiteSettings.get_settings()
        serializer = SiteSettingsSerializer(s, context={'request': request})
        return Response(serializer.data)
