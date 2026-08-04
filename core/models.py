from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, blank=True, default='منصة فطنة')
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    site_primary_color = models.CharField(max_length=7, blank=True, default='#F5C518')
    site_secondary_color = models.CharField(max_length=7, blank=True, default='#7C3AED')

    # Hero Section
    landing_hero_title = models.CharField(max_length=255, default='منصة فطنة')
    landing_hero_subtitle = models.TextField(blank=True, default='نُعدّهم للحياة، لا للامتحانات!')
    landing_hero_button_text = models.CharField(max_length=100, default='ابدأ رحلتك الآن 🚀')
    landing_hero_button_url = models.CharField(max_length=255, default='/login')
    landing_hero_image = models.ImageField(upload_to='settings/', blank=True, null=True)

    # Programs
    landing_programs_title = models.CharField(max_length=255, blank=True, default='برامجنا الممتعة ✨')
    landing_programs_json = models.TextField(blank=True, default='[]')

    # Stats
    landing_stats_title = models.CharField(max_length=255, blank=True, default='إنجازاتنا بالأرقام')
    landing_stats_json = models.TextField(blank=True, default='[]')

    # About
    landing_about_title = models.CharField(max_length=255, blank=True, default='من نحن؟')
    landing_about_text = models.TextField(blank=True, default='')
    landing_about_image = models.ImageField(upload_to='settings/', blank=True, null=True)

    # Features
    landing_features_title = models.CharField(max_length=255, blank=True, default='التعلم أصبح أكثر متعة!')
    landing_features_subtitle = models.TextField(blank=True, default='')
    landing_features_json = models.TextField(blank=True, default='[]')

    # How It Works
    landing_how_it_works_title = models.CharField(max_length=255, blank=True, default='كيف يعمل الموقع؟')

    # Testimonials
    landing_testimonials_title = models.CharField(max_length=255, blank=True, default='ماذا يقولون عنا؟')
    landing_testimonials_json = models.TextField(blank=True, default='[]')

    # FAQ
    landing_faq_title = models.CharField(max_length=255, blank=True, default='الأسئلة الشائعة')
    landing_faq_json = models.TextField(blank=True, default='[]')

    # CTA
    landing_cta_title = models.CharField(max_length=255, blank=True, default='جاهز تصنع إنجازك؟')
    landing_cta_text = models.TextField(blank=True, default='')
    landing_cta_button_text = models.CharField(max_length=100, default='ابدأ الآن')
    landing_cta_button_url = models.CharField(max_length=255, default='/login')

    # Footer & Contact
    footer_desc = models.TextField(blank=True, default='')
    footer_text = models.CharField(max_length=255, blank=True, default='جميع الحقوق محفوظة © منصة فطنة')
    contact_email = models.CharField(max_length=255, blank=True, default='')
    contact_phone = models.CharField(max_length=255, blank=True, default='')
    contact_address = models.TextField(blank=True, default='')
    social_whatsapp = models.CharField(max_length=255, blank=True, default='')
    social_facebook = models.CharField(max_length=255, blank=True, default='')
    social_instagram = models.CharField(max_length=255, blank=True, default='')
    social_tiktok = models.CharField(max_length=255, blank=True, default='')

    # SMTP / Email settings
    smtp_host = models.CharField(max_length=255, blank=True, default='')
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.CharField(max_length=255, blank=True, default='')
    smtp_password_encrypted = models.CharField(max_length=255, blank=True, default='')
    smtp_use_tls = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SiteSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
