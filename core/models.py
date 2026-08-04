from django.db import models

DEFAULT_PROGRAMS_JSON = '''[
  {"slug": "quran", "name": "قسم التعليم القرآني", "description": "حفظ وتجويد بطرق تفاعلية مبتكرة لترسيخ القرآن في النفوس.", "icon": "🕌"},
  {"slug": "memory", "name": "الذاكرة الخارقة", "description": "تطوير مهارات الحفظ السريع والاستيعاب الفائق.", "icon": "🧠"},
  {"slug": "soroban", "name": "الحساب الذهني (السوروبان)", "description": "تطوير سرعة الحساب والدقة في حل المسائل المالية والرياضية.", "icon": "🧮"},
  {"slug": "problem-solving", "name": "حل المشكلات والمنطق", "description": "تنمية التفكير النقدي والتحليلي لدى الأطفال.", "icon": "🧩"}
]'''

DEFAULT_FEATURES_JSON = '''[
  {"title": "تحديات يومية", "desc": "أكمل التحديات اليومية واربح نقاط ومكافآت رائعة.", "icon": "🎯"},
  {"title": "نظام الأوسمة", "desc": "احصل على أوسمة تميز عند إتمام كل وحدة تعليمية.", "icon": "👑"},
  {"title": "لوحة الصدارة", "desc": "تنافس مع أصدقائك وتصدر قائمة المبدعين الأسبوعية.", "icon": "🏆"},
  {"title": "شهادات معتمدة", "desc": "احصل على شهادات إنجاز موثقة عند إتمام أي برنامج.", "icon": "📜"}
]'''

DEFAULT_STATS_JSON = '''[
  {"num": 1250, "label": "طالب مبدع", "emoji": "👨‍🎓"},
  {"num": 8, "label": "برامج متخصصة", "emoji": "📚"},
  {"num": 98, "label": "نسبة الرضا", "emoji": "⭐"},
  {"num": 15, "label": "مشرف معتمد", "emoji": "🏆"}
]'''

DEFAULT_TESTIMONIALS_JSON = '''[
  {"name": "أحمد بن علي", "role": "ولي أمر طالب", "text": "منصة فطنة غيّرت حياة ابني تماماً، أصبح يقضي وقته في حفظ القرآن والحساب الذهني بدلاً من الألعاب الإلكترونية."},
  {"name": "مريم البتول", "role": "أم لطالبة", "text": "المحتوى التفاعلي ممتاز جداً والتنافسية محفزة. ابنتي أصبحت أكثر ثقة بنفسها وبشكل ملحوظ."},
  {"name": "ياسين المحمدي", "role": "ولي أمر", "text": "بيئة آمنة ومحتوى هادف، شكراً لفريق منصة فطنة على هذا العمل العظيم."}
]'''

DEFAULT_FAQ_JSON = '''[
  {"q": "كيف يمكن تسجيل ابني في المنصة؟", "a": "يمكنك الضغط على زر ابدأ الآن واختيار البرنامج المناسب وإدخال معلومات الطالب."},
  {"q": "هل المحتوى مناسب لجميع الأعمار؟", "a": "نعم، البرامج مخصصة للأطفال والناشئة من سن 9 إلى 18 سنة بمستويات تدرجية."},
  {"q": "هل تقدم المنصة شهادات إتمام؟", "a": "نعم، يحصل الطالب على شهادة إتمام معتمدة فور إكمال كافة متطلبات البرنامج التعليمي."}
]'''

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
    landing_programs_json = models.TextField(blank=True, default=DEFAULT_PROGRAMS_JSON)

    # Stats
    landing_stats_title = models.CharField(max_length=255, blank=True, default='إنجازاتنا بالأرقام')
    landing_stats_json = models.TextField(blank=True, default=DEFAULT_STATS_JSON)

    # About
    landing_about_title = models.CharField(max_length=255, blank=True, default='من نحن؟')
    landing_about_text = models.TextField(blank=True, default='نرى اليوم واقعاً مؤلماً؛ أطفال صغار تائهون بين شاشات الهواتف. من هذا الألم، وُلدت فكرة منصة فطنة لتقديم بديل آمن وتربوي ممتع.')
    landing_about_image = models.ImageField(upload_to='settings/', blank=True, null=True)

    # Features
    landing_features_title = models.CharField(max_length=255, blank=True, default='التعلم أصبح أكثر متعة!')
    landing_features_subtitle = models.TextField(blank=True, default='تجربة تعليمية تفاعلية مليئة بالألعاب والتحديات والمكافآت لتحفزك كل يوم على التقدم والتعلم.')
    landing_features_json = models.TextField(blank=True, default=DEFAULT_FEATURES_JSON)

    # How It Works
    landing_how_it_works_title = models.CharField(max_length=255, blank=True, default='كيف يعمل الموقع؟')

    # Testimonials
    landing_testimonials_title = models.CharField(max_length=255, blank=True, default='ماذا يقولون عنا؟')
    landing_testimonials_json = models.TextField(blank=True, default=DEFAULT_TESTIMONIALS_JSON)

    # FAQ
    landing_faq_title = models.CharField(max_length=255, blank=True, default='الأسئلة الشائعة')
    landing_faq_json = models.TextField(blank=True, default=DEFAULT_FAQ_JSON)

    # CTA
    landing_cta_title = models.CharField(max_length=255, blank=True, default='جاهز تصنع إنجازك؟')
    landing_cta_text = models.TextField(blank=True, default='انضم إلى آلاف الطلاب واستمتع بتجربة تعليمية فريدة.')
    landing_cta_button_text = models.CharField(max_length=100, default='ابدأ الآن')
    landing_cta_button_url = models.CharField(max_length=255, default='/login')

    # Footer & Contact
    footer_desc = models.TextField(blank=True, default='منصة تعليمية تربوية تهدف لتأسيس أطفالنا وتطوير مهاراتهم باللعب والتفاعل.')
    footer_text = models.CharField(max_length=255, blank=True, default='جميع الحقوق محفوظة © منصة فطنة')
    contact_email = models.CharField(max_length=255, blank=True, default='contact@fitna.dz')
    contact_phone = models.CharField(max_length=255, blank=True, default='+213795375422')
    contact_address = models.TextField(blank=True, default='الجزائر العاصمة، الجزائر')
    social_whatsapp = models.CharField(max_length=255, blank=True, default='+213773650836')
    social_facebook = models.CharField(max_length=255, blank=True, default='https://facebook.com')
    social_instagram = models.CharField(max_length=255, blank=True, default='https://instagram.com')
    social_tiktok = models.CharField(max_length=255, blank=True, default='https://tiktok.com')

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
        # Ensure default rich JSONs if fields were empty or '[]'
        updated = False
        if not obj.landing_programs_json or obj.landing_programs_json == '[]':
            obj.landing_programs_json = DEFAULT_PROGRAMS_JSON
            updated = True
        if not obj.landing_features_json or obj.landing_features_json == '[]':
            obj.landing_features_json = DEFAULT_FEATURES_JSON
            updated = True
        if not obj.landing_stats_json or obj.landing_stats_json == '[]':
            obj.landing_stats_json = DEFAULT_STATS_JSON
            updated = True
        if not obj.landing_testimonials_json or obj.landing_testimonials_json == '[]':
            obj.landing_testimonials_json = DEFAULT_TESTIMONIALS_JSON
            updated = True
        if not obj.landing_faq_json or obj.landing_faq_json == '[]':
            obj.landing_faq_json = DEFAULT_FAQ_JSON
            updated = True
        if updated:
            obj.save()
        return obj
