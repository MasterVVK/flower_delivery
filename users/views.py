from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from .forms import CustomUserCreationForm
from orders.models import Product, Cart, CartItem
from .models import Address
from django.contrib import messages
from dadata import Dadata
import logging

logger = logging.getLogger('my_custom_logger')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            session_key = request.session.session_key

            logger.info(f"Session key before login: {session_key}")

            guest_cart_items = []
            if session_key:
                try:
                    guest_cart = Cart.objects.get(session_key=session_key)
                    guest_cart_items = [{'product_id': item.product.id, 'quantity': item.quantity} for item in guest_cart.items.all()]
                    logger.info(f"Guest cart items: {guest_cart_items}")
                except Cart.DoesNotExist:
                    logger.info("Guest cart does not exist")

            login(request, user)

            logger.info(f"Session key after login: {request.session.session_key}")

            if guest_cart_items:
                user_cart, created = Cart.objects.get_or_create(user=user)
                for item in guest_cart_items:
                    product = get_object_or_404(Product, id=item['product_id'])
                    cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
                    if not created:
                        cart_item.quantity += item['quantity']
                    cart_item.save()
                logger.info(f"User cart items after merging: {list(user_cart.items.all())}")

            # Обработка параметра next
            next_url = request.POST.get('next') or request.GET.get('next')
            if not next_url or next_url == 'index':  # Если next пуст или равен главной странице
                next_url = 'index'  # Перенаправляем на главную страницу

            logger.info(f"Redirecting to: {next_url}")

            return redirect(next_url)
    else:
        form = AuthenticationForm()
        next_url = request.GET.get('next', '')
    return render(request, 'users/login.html', {'form': form, 'next': next_url})

@login_required
def profile(request):
    addresses = request.user.addresses.all()
    return render(request, 'users/profile.html', {'addresses': addresses})

@login_required
def add_address(request):
    if request.method == 'POST':
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        postal_code = request.POST['postal_code']
        country = request.POST['country']
        is_default = 'is_default' in request.POST

        if is_default:
            request.user.addresses.update(is_default=False)

        Address.objects.create(
            user=request.user,
            street=street,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default
        )

        messages.success(request, 'Address added successfully!')
        return redirect('profile')

@login_required
def search_address(request):
    search_query = request.GET.get('search')
    found_addresses = []

    if search_query:
        token = "4d54df628bb209885446263931d4d785955d21d3"
        dadata = Dadata(token)
        result = dadata.suggest("address", search_query)

        for suggestion in result:
            found_addresses.append({
                'value': suggestion['value'],
                'data': suggestion['data']
            })

    return render(request, 'users/profile.html', {'search_query': search_query, 'found_addresses': found_addresses})
