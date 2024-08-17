# flower_delivery/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fileviewer/', include('fileviewer.urls')),
    path('users/', include('users.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('orders.urls')),  # Маршруты для приложения orders
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
