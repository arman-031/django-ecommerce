from django.contrib.auth.backends import ModelBackend
from account.models import User


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            return None
        except User.DoesNotExist:
            return None
