# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from orders.models import Cart, CartItem

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Объединение корзины гостя с корзиной пользователя
            session_key = request.session.session_key
            if session_key:
                try:
                    guest_cart = Cart.objects.get(session_key=session_key)
                    user_cart, created = Cart.objects.get_or_create(user=user)

                    for item in guest_cart.items.all():
                        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=item.product)
                        if not created:
                            cart_item.quantity += item.quantity
                        cart_item.save()

                    guest_cart.delete()  # Удаление сессионной корзины после объединения
                except Cart.DoesNotExist:
                    pass

            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')
