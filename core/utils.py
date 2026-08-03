from django.core.mail import send_mail
from django.conf import settings

def send_account_creation_email(user, raw_password):
    # This is a synchronous function for now.
    # To migrate to Celery later, simply add @shared_task and call .delay()
    subject = "مرحباً بك في منصة فطنة"
    message = f"""
    مرحباً {user.full_name}،
    
    تم إنشاء حسابك بنجاح في منصة فطنة.
    معلومات تسجيل الدخول:
    البريد الإلكتروني: {user.email}
    كلمة المرور: {raw_password}
    
    الرجاء تغيير كلمة المرور بعد تسجيل الدخول.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")

def send_notification_email(title, message, recipient_list):
    try:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send notification email: {e}")
