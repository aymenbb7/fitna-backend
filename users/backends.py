from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
import sys

User = get_user_model()

class UnifiedAuthBackend(ModelBackend):
    """
    Authenticates a user using either their email or username (case-insensitive).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD) or kwargs.get('email')
            
        if username:
            username = str(username).strip()
            
        if not username or not password:
            return None

        try:
            user = User.objects.filter(
                Q(email__iexact=username) | Q(username__iexact=username)
            ).first()
            if not user:
                User().set_password(password)
                return None
        except Exception:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None

