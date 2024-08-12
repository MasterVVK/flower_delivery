from django.contrib import admin
from .models import Product, ProductCategory, Order, OrderProduct, Review, Report

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']
    search_fields = ['name']
    list_filter = ['category']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderProductInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_sales', 'total_orders']
    list_filter = ['date']
