import os
import requests
from django.conf import settings
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display

def setup_arabic_font():
    font_name = 'Helvetica'
    try:
        font_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'fonts')
        font_path = os.path.join(font_dir, 'Amiri-Regular.ttf')
        
        if not os.path.exists(font_path):
            os.makedirs(font_dir, exist_ok=True)
            url = 'https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf'
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                with open(font_path, 'wb') as f:
                    f.write(res.content)
                    
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Arabic', font_path))
            font_name = 'Arabic'
    except Exception as e:
        print("PDF Font Registration Warning:", e)
        font_name = 'Helvetica'
        
    return font_name

def render_arabic(text, font_name='Arabic'):
    if not text:
        return ''
    text_str = str(text)
    if font_name == 'Arabic':
        try:
            return get_display(arabic_reshaper.reshape(text_str))
        except Exception:
            return text_str
    return text_str
