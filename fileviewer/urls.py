from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_files, name='list_files'),
    path('view/<path:path>/', views.view_file, name='view_file'),
]
