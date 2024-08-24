# users/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('set_default_address/', views.set_default_address, name='set_default_address'),
    path('add_address/', views.add_address, name='add_address'),
    path('add_address_page/', views.add_address_page, name='add_address_page'),
    path('search_address/', views.search_address, name='search_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('delete_selected_addresses/', views.delete_selected_addresses, name='delete_selected_addresses'),
]
