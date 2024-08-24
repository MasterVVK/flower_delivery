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
    default_address = request.user.addresses.filter(is_default=True).first()
    return render(request, 'users/profile.html', {
        'addresses': addresses,
        'default_address': default_address
    })

@login_required
def set_default_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('default_address')
        if address_id:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            Address.objects.filter(id=address_id, user=request.user).update(is_default=True)
            messages.success(request, 'Адрес по умолчанию обновлен.')
    return redirect('profile')

@login_required
def add_address_page(request):
    return render(request, 'users/add_address.html')


@login_required
def add_address(request):
    if request.method == 'POST':
        full_address = request.POST['full_address']
        is_default = 'is_default' in request.POST

        # Используем данные из результата поиска (suggest)
        token = "4d54df628bb209885446263931d4d785955d21d3"
        dadata = Dadata(token)

        try:
            result = dadata.suggest("address", full_address)
            if not result:
                messages.error(request, "Адрес не найден.")
                return redirect('add_address_page')

            # Берем первый результат из suggest
            suggestion = result[0]['data']

            # Извлекаем данные из результата
            street = suggestion.get('street_with_type', '')
            city = suggestion.get('city', '')
            state = suggestion.get('region', '')
            postal_code = suggestion.get('postal_code', '')
            country = suggestion.get('country', 'Россия')

        except Exception as e:
            logger.error(f"Неизвестная ошибка: {str(e)}")
            messages.error(request, "Произошла ошибка при обработке вашего запроса.")
            return redirect('add_address_page')

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

        messages.success(request, 'Адрес добавлен успешно.')
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

    return render(request, 'users/add_address.html', {'search_query': search_query, 'found_addresses': found_addresses})

@login_required
def delete_address(request, address_id):
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        messages.success(request, 'Адрес успешно удален.')
    except Exception as e:
        logger.error(f"Ошибка при удалении адреса: {str(e)}")
        messages.error(request, 'Произошла ошибка при удалении адреса.')
    return redirect('profile')

@login_required
def delete_selected_addresses(request):
    if request.method == 'POST':
        addresses_to_delete = request.POST.getlist('addresses_to_delete')
        if addresses_to_delete:
            Address.objects.filter(id__in=addresses_to_delete, user=request.user).delete()
            messages.success(request, 'Выбранные адреса успешно удалены.')
        else:
            messages.error(request, 'Пожалуйста, выберите хотя бы один адрес для удаления.')
    return redirect('profile')
