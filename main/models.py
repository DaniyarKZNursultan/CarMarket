import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

KAZAKHSTAN_CITIES = [
    ("Almaty", "Алматы"),
    ("Astana", "Астана"),
    ("Shymkent", "Шымкент"),
    ("Karaganda", "Караганда"),
    ("Aktobe", "Актобе"),
    ("Taraz", "Тараз"),
    ("Pavlodar", "Павлодар"),
    ("Ust-Kamenogorsk", "Усть-Каменогорск"),
    ("Semey", "Семей"),
    ("Atyrau", "Атырау"),
    ("Kostanay", "Костанай"),
    ("Petropavl", "Петропавловск"),
    ("Aktau", "Актау"),
    ("Kyzylorda", "Кызылорда"),
    ("Oral", "Уральск"),
    ("Turkistan", "Туркестан"),
    ("Kokshetau", "Кокшетау"),
    ("Taldykorgan", "Талдыкорган"),
    ("Zhezkazgan", "Жезказган"),
]

class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Покупатель'
        DEALERSHIP_EMPLOYEE = 'dealer_employee', 'Сотрудник автосалона'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    auto_center = models.ForeignKey(
        'AutoCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    def save(self, *args, **kwargs):
        if not self.username:
            base = self.email or self.phone or str(uuid.uuid4())
            self.username = slugify(base).replace('.', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class AutoCenter(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, choices=KAZAKHSTAN_CITIES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    images = models.ImageField(upload_to='autocenters/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class CarBrand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brand_logos/')
    description = models.TextField(blank=True)
    auto_centers = models.ManyToManyField('AutoCenter', related_name='brands')

    def __str__(self):
        return self.name

class Car(models.Model):
    class DriveType(models.TextChoices):
        FWD = "FWD", "Передний"
        RWD = "RWD", "Задний"
        AWD = "AWD", "Полный"

    class TransmissionType(models.TextChoices):
        MANUAL = "MT", "Механика"
        AUTOMATIC = "AT", "Автомат"
        CVT = "CVT", "Вариатор"
        DCT = "DCT", "Робот"

    class BodyType(models.TextChoices):
        SEDAN = "sedan", "Седан"
        HATCHBACK = "hatchback", "Хэтчбек"
        SUV = "suv", "Внедорожник (SUV)"
        COUPE = "coupe", "Купе"
        CONVERTIBLE = "convertible", "Кабриолет"
        WAGON = "wagon", "Универсал"
        PICKUP = "pickup", "Пикап"
        VAN = "van", "Фургон"
        MINIVAN = "minivan", "Минивэн"
        LIFTBACK = "liftback", "Лифтбэк"
        FASTBACK = "fastback", "Фастбэк"
        ROADSTER = "roadster", "Родстер"
        TARGA = "targa", "Тарга"
        CROSSOVER = "crossover", "Кроссовер"
        MICROCAR = "microcar", "Микроавтомобиль"
        LIMOUSINE = "limousine", "Лимузин"
        PANEL_VAN = "panel_van", "Грузовой фургон"

    class EngineType(models.TextChoices):
        GASOLINE = "gasoline", "Бензиновый"
        DIESEL = "diesel", "Дизельный"
        HYBRID = "hybrid", "Гибрид"
        EV = "EV", "Электрический"
        LPG = "lpg", "Газ (LPG)"

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=100, choices=KAZAKHSTAN_CITIES)
    body_type = models.CharField(max_length=50, choices=BodyType.choices)
    engine = models.CharField(max_length=20, choices=EngineType.choices)
    engine_capacity = models.DecimalField(max_digits=3, decimal_places=1)
    transmission = models.CharField(max_length=10, choices=TransmissionType.choices)
    drive = models.CharField(max_length=10, choices=DriveType.choices)
    color = models.CharField(max_length=50)
    steering_wheel = models.CharField(max_length=20, choices=[("left", "Левый"), ("right", "Правый")])
    customs_cleared = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    credit_available = models.BooleanField(default=False)

    class Meta:
        abstract = True


class UsedCar(Car):
    mileage = models.PositiveIntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="used_cars", null=True)

    def preview_image(self):
        first_image = self.images.first()
        return first_image.image.url if first_image else None



class CarImage(models.Model):
    car = models.ForeignKey(UsedCar, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/')


class NewCar(Car):
    vin = models.CharField(max_length=17, unique=True)
    warranty_years = models.PositiveIntegerField(default=3)
    in_stock = models.BooleanField(default=True)
    auto_center = models.ForeignKey(AutoCenter, on_delete=models.CASCADE, null=False, blank=False, default=1)  # Укажите ID существующего автосалона
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)  # Для модерации объявлений
    
    class Meta:
        verbose_name = "Новое авто"
        verbose_name_plural = "Новые авто"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
    
    def preview_image(self):
        first_image = self.images.first()
        return first_image.image.url if first_image else None
    

class NewCarImage(models.Model):
    car = models.ForeignKey(NewCar, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='new_cars/')

    def __str__(self):
            return f"Image for {self.car.brand} {self.car.model}"
    
