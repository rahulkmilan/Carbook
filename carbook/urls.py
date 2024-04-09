"""
URL configuration for carbook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from app1 import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', views.index),
    path('',views.profile , name='profile'),
    path('index',views.index),
    path('login',views.login,name='login'),
    path('logout',views.logout),
    path('customer-reg',views.reg_customer),
    # path('customer-log',views.profile),
    path('dealer-reg',views.reg_dealer),
    path('dealer-log',views.add_car),
    path('accept_car', views.accept_car, name='accept_car'),
    path('reject_car', views.reject_car, name='reject_car'),
    # path('admin-log', views.profile), 
    # path('customer-log', views.profile),
    path('book/<str:regno>', views.book, name='book'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('delete-car/<int:car_id>/', views.delete_car, name='delete_car'),



    path('password_reset/',views.password_reset,name='password_reset'),
    path('password_reset/done/',views.password_reset_done,name='password_reset_done'),
    path('reset/<uidb64>/<token>/',views.password_reset_confirm,name='password_reset_confirm'),
    path('reset/expired',views.reset_link_expired,name='reset_link_expired'),

    
    path('contact',views.contact),
    path('payment',views.payment,name='payment'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('edit_car_field/<int:car_id>/', views.edit_car_field, name='edit_car_field'),
    path('change-booking-status/<int:booking_id>/', views.change_booking_status, name='change_booking_status'),
    path('deactivate_dealer/<int:dealer_id>/', views.deactivate_dealer, name='deactivate_dealer'),
    path('deactivate_customer/<int:customer_id>/', views.deactivate_customer, name='deactivate_customer'),
    path('suspend_car/<int:car_id>/', views.suspend_car, name='suspend_car'),

    # path('payment-status', views.payment, name='payment-status'),
    # path('', views.car_list, name='car_list'),
    # path('filter-cars/', views.filter_cars, name='filter_cars'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)