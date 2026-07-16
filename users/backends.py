from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class UnifiedAuthBackend(ModelBackend):
    """
    Authenticates a user using either their email or username.
    This replaces the need for multiple backends and guarantees that both
    fields are checked reliably during the login process.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            
        if not username:
            return None

        try:
            # Check both email and username in a single query
            user = User.objects.get(Q(email=username) | Q(username=username))
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # In case someone somehow has a username that is the same as someone else's email
            user = User.objects.filter(Q(email=username) | Q(username=username)).first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None

