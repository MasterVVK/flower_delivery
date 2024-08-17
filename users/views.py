# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from orders.models import Product, Cart, CartItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sessions.models import Session

import logging

#logger = logging.getLogger(__name__)

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
            session_key = request.session.session_key

            # Логгирование текущей сессии
            logging.info(f"Session key before login: {session_key}")

            guest_cart_items = []
            if session_key:
                try:
                    guest_cart = Cart.objects.get(session_key=session_key)
                    guest_cart_items = [{'product_id': item.product.id, 'quantity': item.quantity} for item in guest_cart.items.all()]
                    logging.info(f"Guest cart items: {guest_cart_items}")
                except Cart.DoesNotExist:
                    logging.info("Guest cart does not exist")

            # Логиним пользователя
            login(request, user)

            # Логгирование новой сессии
            logging.info(f"Session key after login: {request.session.session_key}")

            if guest_cart_items:
                user_cart, created = Cart.objects.get_or_create(user=user)
                for item in guest_cart_items:
                    product = get_object_or_404(Product, id=item['product_id'])
                    cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
                    if not created:
                        cart_item.quantity += item['quantity']
                    cart_item.save()
                logging.info(f"User cart items after merging: {list(user_cart.items.all())}")

            next_url = request.POST.get('next', 'index')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})



@login_required
def profile(request):
    return render(request, 'users/profile.html')
