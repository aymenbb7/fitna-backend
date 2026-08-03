from django.db import models

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default='منصة فطنة')
    logo_url = models.URLField(blank=True, null=True)
    
    # Hero Section
    landing_hero_title = models.CharField(max_length=255, default='منصة فطنة')
    landing_hero_subtitle = models.CharField(max_length=255, default='نُعدّهم للحياة، لا للامتحانات!')
    landing_hero_button_text = models.CharField(max_length=100, default='ابدأ رحلتك الآن 🚀')
    landing_hero_button_url = models.CharField(max_length=255, default='/login')
    
    # Programs
    landing_programs_title = models.CharField(max_length=255, default='برامجنا الممتعة ✨')
    
    # Stats
    landing_stats_title = models.CharField(max_length=255, default='إنجازاتنا بالأرقام')
    landing_stats_json = models.TextField(default='[]', help_text="JSON array of stats objects")
    
    # About
    landing_about_title = models.CharField(max_length=255, default='من نحن؟')
    landing_about_text = models.TextField(blank=True, null=True)
    
    # Features
    landing_features_title = models.CharField(max_length=255, default='التعلم أصبح أكثر متعة!')
    landing_features_subtitle = models.TextField(blank=True, null=True)
    landing_features_json = models.TextField(default='[]', help_text="JSON array of features")
    
    # How It Works
    landing_how_it_works_title = models.CharField(max_length=255, default='كيف يعمل الموقع؟')
    landing_programs_json = models.TextField(default='[]', help_text="JSON array for how it works")
    
    # Testimonials
    landing_testimonials_title = models.CharField(max_length=255, default='ماذا يقولون عنا؟')
    landing_testimonials_json = models.TextField(default='[]', help_text="JSON array of testimonials")
    
    # FAQ
    landing_faq_title = models.CharField(max_length=255, default='الأسئلة الشائعة')
    landing_faq_json = models.TextField(default='[]', help_text="JSON array of FAQs")
    
    # CTA
    landing_cta_title = models.CharField(max_length=255, default='جاهز تصنع إنجازك؟')
    landing_cta_text = models.TextField(blank=True, null=True)
    landing_cta_button_text = models.CharField(max_length=100, default='ابدأ الآن')
    landing_cta_button_url = models.CharField(max_length=255, default='/login')
    
    # Footer & Contact
    footer_desc = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(default='contact@fitna.dz')
    social_whatsapp = models.CharField(max_length=50, default='+213000000000')
    social_facebook = models.URLField(blank=True, null=True)
    social_instagram = models.URLField(blank=True, null=True)
    
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
