from django.core.management.base import BaseCommand
from core.models import SiteSettings
import json

class Command(BaseCommand):
    help = 'Seed initial SiteSettings data'

    def handle(self, *args, **options):
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        
        settings.site_name = 'منصة فطنة'
        settings.landing_hero_title = 'منصة فطنة'
        settings.landing_hero_subtitle = 'نُعدّهم للحياة، لا للامتحانات!'
        settings.landing_hero_button_text = 'ابدأ رحلتك الآن 🚀'
        settings.landing_hero_button_url = '/login'
        settings.landing_programs_title = 'برامجنا الممتعة ✨'
        
        # Stats
        settings.landing_stats_title = 'إنجازاتنا بالأرقام'
        settings.landing_stats_json = json.dumps([
            { "num": 1250, "label": "طالب وطالبة", "emoji": "😊", "glow": "rgba(59,130,246,0.5)", "prefix": "+" },
            { "num": 12, "label": "برنامج تدريبي", "emoji": "🏆", "glow": "rgba(245,197,24,0.5)", "prefix": "+" },
            { "num": 25, "label": "مدرب مميز", "emoji": "🎓", "glow": "rgba(139,92,246,0.5)", "prefix": "+" },
            { "num": 98, "label": "نسبة رضا الطلاب", "emoji": "⭐", "glow": "rgba(16,185,129,0.5)", "suffix": "%" }
        ], ensure_ascii=False)
        
        # About
        settings.landing_about_title = 'من نحن؟'
        settings.landing_about_text = 'نرى اليوم واقعاً مؤلماً؛ أطفال صغار تائهون بين شاشات الهواتف، يضيع وقتهم ويهدر ذكاؤهم في محتويات تافهة لا تسمن ولا تغني من جوع.\n\nمن هذا الألم، وُلدت فكرة «منصة فطنة». لم نرد أن نكتفي بالشكوى، بل صممنا حلاً عملياً يمثل بديلاً آمناً، ذكياً، وجذاباً.\n\nفطنة ليست مجرد منصة تعليمية، بل هي بيئة متكاملة تهدف إلى احتضان شغف الأطفال وإشغالهم بما ينفعهم، لبناء مهاراتهم وتأسيس مستقبل مشرق لهم، بعيداً عن مخاطر الفراغ الرقمي.'
        
        # Features
        settings.landing_features_title = 'التعلم أصبح أكثر متعة!'
        settings.landing_features_subtitle = 'تجربة تعليمية تفاعلية مليئة بالألعاب والتحديات والمكافآت لتحفزك كل يوم على التقدم والتعلم.'
        settings.landing_features_json = json.dumps([
            { "title": 'تحديات يومية', "desc": 'أكمل التحديات اليومية واربح نقاط ومكافآت رائعة.', "icon": '🎯', "color": 'text-blue-400', "bg": 'bg-blue-400/10' },
            { "title": 'نظام النقاط', "desc": 'اجمع النقاط، ارتقِ في المستويات، وكن الأفضل!', "icon": '🏆', "color": 'text-accentGold', "bg": 'bg-yellow-400/10' },
            { "title": 'شهادات وإنجازات', "desc": 'احصل على شهادات معتمدة وشارك إنجازاتك مع أصدقائك.', "icon": '🏅', "color": 'text-green-400', "bg": 'bg-green-400/10' },
            { "title": 'متابعة أولياء الأمور', "desc": 'تابع تقدم أبنائك وتعرف على تقارير تفصيلية بسهولة.', "icon": '👥', "color": 'text-pink-400', "bg": 'bg-pink-400/10' }
        ], ensure_ascii=False)
        
        # How It Works
        settings.landing_how_it_works_title = 'كيف يعمل الموقع؟'
        settings.landing_programs_json = json.dumps([
            { "num": 1, "text": "سجّل حسابك في المنصة كطالب مجاناً بخطوات بسيطة.", "color": "#3B82F6" },
            { "num": 2, "text": "تصفح الوحدات والبرامج المتاحة واختر ما يناسبك.", "color": "#F5C518" },
            { "num": 3, "text": "أتمم عملية الدفع بسهولة وتواصل مع المشرف للتفعيل.", "color": "#10B981" },
            { "num": 4, "text": "ابدأ التعلم واستمتع بالدروس التفاعلية والمحتوى الثري.", "color": "#EF4444" }
        ], ensure_ascii=False)
        
        # Testimonials
        settings.landing_testimonials_title = 'ماذا يقولون عنا؟'
        settings.landing_testimonials_json = json.dumps([
            { "name": "أم أحمد", "role": "ولية أمر", "text": "لاحظت تغييراً كبيراً في شخصية ابني بعد انضمامه لبرنامج حل المشكلات. أنصح بها بشدة!" },
            { "name": "ياسين", "role": "طالب (16 سنة)", "text": "البرامج هنا مختلفة تماماً عن المدرسة، نتعلم أشياء تفيدنا في حياتنا اليومية بشكل ممتع." },
            { "name": "أ. محمد", "role": "أستاذ رياضيات", "text": "طريقة تقديم المعلومات في فطنة مبتكرة وتجعل التعلم ممتعاً. منصة رائعة فعلاً." }
        ], ensure_ascii=False)
        
        # FAQ
        settings.landing_faq_title = 'الأسئلة الشائعة'
        settings.landing_faq_json = json.dumps([
            { "q": "هل هناك شهادات معتمدة؟", "a": "نعم، يحصل الطالب على شهادة إتمام بعد اجتياز متطلبات كل برنامج بنجاح." },
            { "q": "ما هي طرق الدفع المتاحة؟", "a": "نوفر الدفع عبر البطاقة الذهبية، التحويل البنكي (بريد الجزائر)، الدفع نقداً، وتطبيقات أخرى." },
            { "q": "هل الدروس مباشرة أم مسجلة؟", "a": "نعتمد نظاماً يجمع بين الجلسات المباشرة التفاعلية والدروس المسجلة للمراجعة في أي وقت." }
        ], ensure_ascii=False)
        
        # CTA
        settings.landing_cta_title = 'جاهز تصنع إنجازك؟'
        settings.landing_cta_text = 'انضم الآن إلى آلاف الطلاب وابدأ رحلتك مع فطنة نحو التميز والإبداع!\nالمستقبل بانتظارك، لا تدع الفرصة تفوتك.'
        settings.landing_cta_button_text = 'ابدأ الآن'
        settings.landing_cta_button_url = '/login'
        
        # Footer
        settings.footer_desc = 'فريقنا مستعد دائماً للإجابة على استفساراتكم ومساعدتكم في اختيار البرنامج الأنسب لأبنائكم.'
        settings.contact_email = 'contact@fitna.dz'
        settings.social_whatsapp = '+213700000000'
        
        settings.save()
        self.stdout.write(self.style.SUCCESS('Successfully seeded SiteSettings data'))
