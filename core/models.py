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
    landing_hero_title = models.CharField(max_length=255, blank=True, default='منصة فطنة')
    landing_hero_subtitle = models.TextField(blank=True, default='')
    landing_hero_button_text = models.CharField(max_length=100, blank=True, default='ابدأ الآن')
    landing_hero_button_url = models.CharField(max_length=255, blank=True, default='/login')
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
    landing_cta_button_text = models.CharField(max_length=100, blank=True, default='ابدأ الآن')
    landing_cta_button_url = models.CharField(max_length=255, blank=True, default='/login')

    # Footer & Contact
    footer_desc = models.TextField(blank=True, default='منصة تعليمية تربوية تهدف لتأسيس أطفالنا وتطوير مهاراتهم باللعب والتفاعل.')
    footer_text = models.CharField(max_length=255, blank=True, default='جميع الحقوق محفوظة © منصة فطنة')
    contact_email = models.CharField(max_length=255, blank=True, default='info@fitna.dz')
    contact_phone = models.CharField(max_length=255, blank=True, default='+213773650836')
    contact_address = models.TextField(blank=True, default='الجزائر العاصمة')
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
        
        if not obj.contact_email or obj.contact_email == 'contact@fitna.dz':
            obj.contact_email = 'info@fitna.dz'
        if not obj.contact_phone or '795' in str(obj.contact_phone):
            obj.contact_phone = '+213773650836'
        if not obj.contact_address or obj.contact_address == 'الجزائر العاصمة، الجزائر':
            obj.contact_address = 'الجزائر العاصمة'
        if not obj.social_whatsapp or '795' in str(obj.social_whatsapp) or '0773650836' in str(obj.social_whatsapp):
            obj.social_whatsapp = '+213773650836'

        # Ensure hero and about sections have non-empty defaults matching the homepage
        if not obj.landing_hero_title:
            obj.landing_hero_title = 'منصة فطنة'
        if not obj.landing_hero_subtitle:
            obj.landing_hero_subtitle = 'نُعدّهم للحياة، لا للامتحانات!'
        if not obj.landing_hero_button_text:
            obj.landing_hero_button_text = 'ابدأ رحلتك الآن 🚀'
        if not obj.landing_hero_button_url:
            obj.landing_hero_button_url = '#programs'
        if not obj.landing_about_title:
            obj.landing_about_title = 'من نحن؟'
        if not obj.landing_about_text or 'نرى اليوم واقعاً مؤلماً؛ أطفال صغار تائهون بين شاشات الهواتف. من هذا الألم، وُلدت فكرة منصة فطنة لتقديم بديل آمن وتربوي ممتع.' in obj.landing_about_text or obj.landing_about_text == '':
            obj.landing_about_text = """أطفالنا يستحقون أفضل من هذا

نرى اليوم واقعاً مؤلماً؛ أطفال صغار تائهون بين شاشات الهواتف، يضيع وقتهم ويهدر ذكاؤهم في محتويات تافهة لا تسمن ولا تغني من جوع. المشكلة تتفاقم يوماً بعد يوم، وبتنا نسمع عن حوادث وجرائم يقع ضحيتها أطفالنا بسبب هذا الواقع المفتوح والخطير.

من هذا الألم، وُلدت فكرة «منصة فطنة». لم نرد أن نكتفي بالشكوى، بل صممنا حلاً عملياً يمثل بديلاً آمناً، ذكياً، وجذاباً.

فطنة ليست مجرد منصة تعليمية، بل هي بيئة متكاملة تهدف إلى احتضان شغف الأطفال وإشغالهم بما ينفعهم، لبناء مهاراتهم وتأسيس مستقبل مشرق لهم، بعيداً عن مخاطر الفراغ الرقمي."""

        if not obj.landing_programs_json or obj.landing_programs_json == '[]':
            obj.landing_programs_json = DEFAULT_PROGRAMS_JSON
        if not obj.landing_features_json or obj.landing_features_json == '[]':
            obj.landing_features_json = DEFAULT_FEATURES_JSON
        if not obj.landing_stats_json or obj.landing_stats_json == '[]':
            obj.landing_stats_json = DEFAULT_STATS_JSON
        if not obj.landing_testimonials_json or obj.landing_testimonials_json == '[]':
            obj.landing_testimonials_json = DEFAULT_TESTIMONIALS_JSON
        if not obj.landing_faq_json or obj.landing_faq_json == '[]':
            obj.landing_faq_json = DEFAULT_FAQ_JSON
            
        obj.save()
        return obj
