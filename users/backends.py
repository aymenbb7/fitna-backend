from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
import sys

User = get_user_model()

class UnifiedAuthBackend(ModelBackend):
    """
    Authenticates a user using either their email or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"--- UNIFIED AUTH LOG ---", file=sys.stderr)
        print(f"1. authenticate() called", file=sys.stderr)
        print(f"2. DB used: {settings.DATABASES['default']['NAME']}", file=sys.stderr)
        
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            
        if username:
            username = username.strip()
            
        print(f"3. username received: {username!r}", file=sys.stderr)
            
        if not username:
            print(f"4. username is empty, returning None", file=sys.stderr)
            return None

        try:
            print(f"5. querying for email or username", file=sys.stderr)
            user = User.objects.get(Q(email=username) | Q(username=username))
            print(f"6. user found: {user} | is_staff: {user.is_staff} | is_active: {user.is_active}", file=sys.stderr)
        except User.DoesNotExist:
            print(f"6. user DOES NOT EXIST", file=sys.stderr)
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            print(f"6. MULTIPLE USERS RETURNED", file=sys.stderr)
            user = User.objects.filter(Q(email=username) | Q(username=username)).first()

        password_matched = user.check_password(password)
        print(f"7. check_password('{password}'): {password_matched}", file=sys.stderr)
        
        if password_matched and self.user_can_authenticate(user):
            print(f"8. Login successful! Returning user.", file=sys.stderr)
            return user
            
        print(f"8. Login failed. user_can_authenticate: {self.user_can_authenticate(user)}", file=sys.stderr)
        return None

