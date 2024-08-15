from django.urls import path
from . import views

urlpatterns = [
    path('manage_products/', views.manage_products, name='manage_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('order/create/<int:product_id>/', views.order_create, name='order_create'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    path('categories/', views.categories, name='categories'),
    path('', views.index, name='index'),
    path('api/products/', views.load_more_products, name='load_more_products'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),  # Добавлен маршрут для оформления заказа
 ]
