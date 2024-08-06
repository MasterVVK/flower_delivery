from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('order/create/<int:product_id>/', views.order_create, name='order_create'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
]
