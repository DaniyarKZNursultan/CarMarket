from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'),

    path('used-cars/', views.used_cars, name='used_cars'),
    path('used_car/<int:car_id>/', views.used_car_detail, name='used_car_detail'),
    path('used-cars/create/', views.create_used_car, name='create_used_car'),
    path('used_car/<int:id>/delete/', views.delete_used_car, name='delete_used_car'),

    path('new-cars/', views.NewCarPageView.as_view(), name='new_cars'),
    path('new-cars/create/', views.create_new_car, name='create_new_car'),

    path('dealer/dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('dealer/new-car/', views.create_new_car, name='create_new_car'),
    path('dealer/car/<int:pk>/edit/', views.edit_car, name='edit_car'),
    path('dealer/car/<int:car_id>/delete/', views.delete_car, name='delete_car'),

    path('dealership/<int:pk>/', views.dealership_detail, name='dealership_detail'),
]
