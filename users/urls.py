# users/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('add_address/', views.add_address, name='add_address'),
    path('search_address/', views.search_address, name='search_address'),
]
