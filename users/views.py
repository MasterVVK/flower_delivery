# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from orders.models import Cart, CartItem
import logging
logger = logging.getLogger(__name__)

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
            logger.debug(f"User {user.username} logged in")
            login(request, user)

            session_key = request.session.session_key
            if session_key:
                logger.debug(f"Session key after login: {session_key}")
                try:
                    guest_cart = Cart.objects.get(session_key=session_key)
                    user_cart, created = Cart.objects.get_or_create(user=user)
                    logger.debug(f"Merging guest cart {guest_cart.id} into user cart {user_cart.id}")

                    for item in guest_cart.items.all():
                        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=item.product)
                        if not created:
                            cart_item.quantity += item.quantity
                        cart_item.save()
                        logger.debug(f"Item {item.product.name} added to user cart")

                    guest_cart.delete()
                    logger.debug("Guest cart deleted after merging")
                except Cart.DoesNotExist:
                    logger.debug("No guest cart found to merge")

            next_url = request.POST.get('next', 'index')
            logger.debug(f"Redirecting to {next_url}")
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')
