from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        print("===> Сигналы загружены!")  # Проверка, что сигналы подгрузились
        import main.signals
