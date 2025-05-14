from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
import requests
from django.core.files.base import ContentFile
from allauth.socialaccount.models import SocialAccount

@receiver(user_logged_in)
def update_google_avatar(request, user, **kwargs):
    print(f"===> Сработал сигнал для {user}")  # Проверка срабатывания сигнала

    # Проверяем, если пользователь вошел через Google
    social_account = SocialAccount.objects.filter(user=user, provider='google').first()
    
    if social_account:
        avatar_url = social_account.extra_data.get('picture')
        if avatar_url:
            avatar_response = requests.get(avatar_url)
            if avatar_response.status_code == 200:
                print(f"===> Аватар получен с URL: {avatar_url}")  # Проверка, что аватар получен

                # Сохраняем аватар в поле avatar
                user.avatar.save(
                    f'{user.username}_google_avatar.jpg',
                    ContentFile(avatar_response.content),
                    save=True
                )
                print(f"===> Аватар сохранён для {user.username}")
