from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from uuid import uuid4
from django.core.exceptions import ValidationError

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        extra_data = sociallogin.account.extra_data

        # Получаем email
        email = extra_data.get('email')

        # Проверяем, если email не был получен
        if not email:
            # Генерируем временный уникальный email
            email = f"social_{uuid4().hex[:10]}@example.com"
        
        # Проверяем, если email уже существует в базе
        if user.__class__.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")

        user.email = email

        # Имя/фамилия
        user.first_name = user.first_name or extra_data.get('given_name', '')
        user.last_name = user.last_name or extra_data.get('family_name', '')

        # Временный номер телефона, если отсутствует
        if not user.phone:
            user.phone = f"social_{uuid4().hex[:10]}"

        # Генерация username, если отсутствует
        if not user.username:
            base_username = (user.first_name + user.last_name).lower() or "user"
            user.username = self.generate_unique_username(base_username)

        user.save()
        return user

    def generate_unique_username(self, base_username):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username
