from django import forms
from .models import Order, Review

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
