from django.forms import modelformset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CarImageFormSet, NewCarFilterForm, NewCarForm, RegistrationForm, LoginForm, UsedCarForm
from django.views.generic import ListView, TemplateView
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import AutoCenter, Car, CarBrand, CarImage, NewCarImage, UsedCar, NewCar, User


def home(request):
    return render(request, 'main/index/index.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def is_dealer(user):
    return user.is_authenticated and user.role == 'dealer_employee'


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            login(request, user)  # Выполняем автоматический вход
            return redirect('home')  # Переход на главную страницу
    else:
        form = RegistrationForm()
    return render(request, 'main/registration/register.html', {'form': form})

@login_required
def profile(request):
    # Получаем все объявления пользователя
    user_ads = UsedCar.objects.filter(owner=request.user)

    context = {
        'user_ads': user_ads,
    }
    
    return render(request, 'main/index/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, 'Профиль успешно обновлён!')
        return redirect('profile')

    return render(request, 'main/index/edit_profile.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Переход на главную страницу
            else:
                form.add_error(None, "Неверный логин или пароль")
    else:
        form = LoginForm()
    return render(request, 'main/registration/login.html', {'form': form})



def used_cars(request):
    cars = UsedCar.objects.all()

    # === ФИЛЬТРАЦИЯ ===
    brand = request.GET.get('brand')
    if brand:
        cars = cars.filter(brand__iexact=brand)

    model = request.GET.get('model')
    if model:
        cars = cars.filter(model__iexact=model)

    city = request.GET.get('city')
    if city:
        cars = cars.filter(city=city)

    price_min = request.GET.get('price_min')
    if price_min:
        cars = cars.filter(price__gte=price_min)

    price_max = request.GET.get('price_max')
    if price_max:
        cars = cars.filter(price__lte=price_max)

    year_min = request.GET.get('year_min')
    if year_min:
        cars = cars.filter(year__gte=year_min)

    year_max = request.GET.get('year_max')
    if year_max:
        cars = cars.filter(year__lte=year_max)

    mileage_max = request.GET.get('mileage_max')
    if mileage_max:
        cars = cars.filter(mileage__lte=mileage_max)

    body_type = request.GET.get('body_type')
    if body_type:
        cars = cars.filter(body_type=body_type)

    engine = request.GET.get('engine')
    if engine:
        cars = cars.filter(engine=engine)

    transmission = request.GET.get('transmission')
    if transmission:
        cars = cars.filter(transmission=transmission)

    drive = request.GET.get('drive')
    if drive:
        cars = cars.filter(drive=drive)

    credit = request.GET.get('credit')
    if credit == 'on':
        cars = cars.filter(credit_available=True)

    customs = request.GET.get('customs')
    if customs == 'on':
        cars = cars.filter(customs_cleared=True)

    # === СОРТИРОВКА ===
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        cars = cars.order_by('price')
    elif sort == 'price_desc':
        cars = cars.order_by('-price')
    elif sort == 'year_desc':
        cars = cars.order_by('-year')
    else:
        cars = cars.order_by('-created_at')

    # === ПАГИНАЦИЯ ===
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # === Передаём choices в шаблон ===
    context = {
        'page_obj': page_obj,
        'filters': request.GET,

        'cities': UsedCar._meta.get_field('city').choices,
        'body_types': UsedCar._meta.get_field('body_type').choices,
        'engines': UsedCar._meta.get_field('engine').choices,
        'transmissions': UsedCar._meta.get_field('transmission').choices,
        'drives': UsedCar._meta.get_field('drive').choices,
    }
    return render(request, 'main/cars/used_cars.html', context)

def used_car_detail(request, car_id):
    # Получаем объект автомобиля по ID
    car = get_object_or_404(UsedCar, id=car_id)
    return render(request, 'main/cars/used_car_detail.html', {'car': car})


@login_required
def create_used_car(request):
    if request.method == 'POST':
        form = UsedCarForm(request.POST, request.FILES)
        formset = CarImageFormSet(request.POST, request.FILES, queryset=CarImage.objects.none())

        if form.is_valid() and formset.is_valid():
            car = form.save(commit=False)
            car.owner = request.user
            car.save()

            images = []
            for image_form in formset:
                if image_form.cleaned_data:
                    image = image_form.save(commit=False)
                    image.car = car
                    images.append(image)

            # Сохраняем все изображения
            for i, img in enumerate(images):
                img.save()
                # если хочешь явно проставлять флаг превью, можно:
                # if i == 0:
                #     img.is_preview = True
                #     img.save()

            return redirect('used_cars')  # ← здесь должен быть name URL-шаблона
    else:
        form = UsedCarForm()
        formset = CarImageFormSet(queryset=CarImage.objects.none())

    return render(request, 'main/cars/create_used_car.html', {
        'form': form,
        'image_formset': formset,
    })


@login_required
def delete_used_car(request, id):
    car = get_object_or_404(UsedCar, id=id, owner=request.user)
    car.delete()
    return redirect('profile')  # Перенаправление обратно в профиль



class NewCarPageView(TemplateView):
    template_name = 'main/cars/new_cars.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = NewCarFilterForm(self.request.GET)
        cars = NewCar.objects.filter(in_stock=True, is_approved=True)  # ← исправлено здесь

        if form.is_valid():
            if form.cleaned_data['brand']:
                cars = cars.filter(brand=form.cleaned_data['brand'].name)
            if form.cleaned_data['city']:
                cars = cars.filter(city=form.cleaned_data['city'])
            if form.cleaned_data['min_price']:
                cars = cars.filter(price__gte=form.cleaned_data['min_price'])
            if form.cleaned_data['max_price']:
                cars = cars.filter(price__lte=form.cleaned_data['max_price'])

        context['form'] = form
        context['filtered_cars'] = cars.order_by('-created_at')
        context['brands'] = CarBrand.objects.all()
        context['popular_cars'] = NewCar.objects.filter(is_approved=True).order_by('-created_at')[:6]  # ← здесь тоже
        context['auto_centers'] = AutoCenter.objects.filter(is_verified=True)
        context['loan_terms'] = [12, 24, 36, 48, 60, 72, 84]

        return context





@login_required
@user_passes_test(is_dealer)
def create_new_car(request):
    if request.method == 'POST':
        form = NewCarForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            car = form.save(commit=False)
            car.created_by = request.user
            car.auto_center = request.user.auto_center
            car.save()

            # Сохраняем изображения
            if 'images' in request.FILES:
                for img in request.FILES.getlist('images'):
                    NewCarImage.objects.create(car=car, image=img)

            return redirect('dealer_dashboard')
    else:
        form = NewCarForm(user=request.user)
    return render(request, 'main/cars/create_new_car.html', {'form': form})


def new_car_detail(request, pk):
    car = get_object_or_404(NewCar, pk=pk)
    return render(request, 'main/cars/new_car_detail.html', {'car': car})



@login_required
@user_passes_test(is_dealer)
def dealer_dashboard(request):
    cars = NewCar.objects.filter(created_by=request.user)
    return render(request, 'main/cars/dealer_dashboard.html', {'cars': cars})


@user_passes_test(is_dealer)
@login_required
def edit_car(request, pk):
    car = get_object_or_404(NewCar, pk=pk)

    # Проверка: пользователь может редактировать только свои авто
    if car.auto_center != request.user.auto_center:
        return HttpResponseForbidden("Вы не можете редактировать это объявление.")

    if request.method == 'POST':
        form = NewCarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect('dealer_dashboard')
    else:
        form = NewCarForm(instance=car)

    return render(request, 'main/cars/edit_car.html', {'form': form, 'car': car})


@user_passes_test(is_dealer)
@login_required
def delete_car(request, car_id):
    car = get_object_or_404(NewCar, id=car_id)

    # Доступ только сотруднику автосалона, которому принадлежит объявление
    if car.auto_center != request.user.auto_center:
        return HttpResponseForbidden("Вы не можете удалить это объявление.")

    if request.method == 'POST':
        car.delete()
        return redirect('dealer_dashboard')

    return render(request, 'dealer/delete_confirm.html', {'car': car})




def dealership_detail(request, pk):
    dealership = get_object_or_404(AutoCenter, pk=pk)
    brands = dealership.brands.all()
    cars = NewCar.objects.filter(auto_center=dealership, is_approved=True)

    # Фильтрация по GET-параметрам
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    year = request.GET.get('year')

    if brand:
        cars = cars.filter(brand=brand)
    if model:
        cars = cars.filter(model=model)
    if year:
        cars = cars.filter(year=year)

    models = NewCar.objects.filter(auto_center=dealership, is_approved=True).values_list('model', flat=True).distinct()
    years = NewCar.objects.filter(auto_center=dealership, is_approved=True).values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'dealership': dealership,
        'brands': brands,
        'cars': cars,
        'models': models,
        'years': years,
    }
    return render(request, 'main/cars/dealership_detail.html', context)
