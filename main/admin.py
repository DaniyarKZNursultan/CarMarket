from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from django import forms

from .models import CarImage, UsedCar, User, AutoCenter


# --- Кастомная форма пользователя ---
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


# --- Кастомная админка пользователя ---
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'role', 'auto_center', 'is_staff', 'is_active')
    list_filter = ('role', 'auto_center', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'avatar', 'role', 'auto_center')}),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)


# --- Inline фото ---
class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ['image']


# --- UsedCar admin ---
class UsedCarAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year', 'price', 'city']
    inlines = [CarImageInline]


# --- Явная регистрация нужных моделей ---
admin.site.register(User, CustomUserAdmin)
admin.site.register(UsedCar, UsedCarAdmin)
admin.site.register(AutoCenter)

# --- Остальные модели регистрируются автоматически ---
app = apps.get_app_config('main')

for model in app.get_models():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
