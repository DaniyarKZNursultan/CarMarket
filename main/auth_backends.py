# yourapp/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Пытаемся найти по email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Если не нашли, ищем по телефону
                user = UserModel.objects.get(phone=username)
            except UserModel.DoesNotExist:
                return None
        
        if user.check_password(password):
            return user
        return None
