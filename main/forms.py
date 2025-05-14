from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import KAZAKHSTAN_CITIES, CarBrand, CarImage, NewCar, User, UsedCar

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Этот номер телефона уже зарегистрирован.')
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован.')
        return email


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)  # Это будет номер телефона или email
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        # Попытка аутентификации с телефонным номером или email
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("Неверный логин или пароль")
        self.user = user
        return cleaned_data
    

class UsedCarForm(forms.ModelForm):
    class Meta:
        model = UsedCar
        exclude = ['created_at', 'updated_at', 'owner']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

CarImageFormSet = forms.modelformset_factory(
    CarImage,
    fields=('image',),
    extra=5,  # Можно изменить на любое количество полей по умолчанию
    widgets={'image': forms.ClearableFileInput(attrs={'multiple': False})}
)


class NewCarFilterForm(forms.Form):
    brand = forms.ModelChoiceField(queryset=CarBrand.objects.all(), required=False, label="Бренд")
    city = forms.ChoiceField(choices=[('', 'Любой город')] + KAZAKHSTAN_CITIES, required=False, label="Город")
    min_price = forms.IntegerField(required=False, label="Цена от")
    max_price = forms.IntegerField(required=False, label="Цена до")


class NewCarForm(forms.ModelForm):
    class Meta:
        model = NewCar
        fields = [
            'brand', 'model', 'year', 'price', 'city',
            'body_type', 'engine', 'engine_capacity', 'transmission',
            'drive', 'color', 'steering_wheel', 'customs_cleared',
            'description', 'credit_available', 'vin', 'warranty_years', 'in_stock'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ← получаем пользователя из аргументов
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'auto_center'):
            self.fields['brand'].queryset = CarBrand.objects.filter(auto_centers=user.auto_center)
        else:
            self.fields['brand'].queryset = CarBrand.objects.none()



