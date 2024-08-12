# flower_delivery/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fileviewer/', include('fileviewer.urls')),
    path('users/', include('users.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('orders.urls')),  # Маршруты для приложения orders
]
