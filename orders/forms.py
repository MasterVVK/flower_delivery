from django import forms
from .models import Product, ProductCategory, Order, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image', 'category', 'description']

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'description']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
