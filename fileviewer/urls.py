from django.urls import path
from . import views

urlpatterns = [
    path('view/<path:path>/', views.view_file, name='view_file'),
    path('<path:path>/', views.list_files, name='list_files'),
    path('', views.list_files, name='list_files'),
]
