from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductCategory, Cart, CartItem, Order, OrderProduct, Review
from .forms import ProductForm, ProductCategoryForm, OrderForm, ReviewForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from .bot_utils import notify_new_order
from django.contrib import messages
from users.models import Address

import logging

logger = logging.getLogger('my_custom_logger')

def get_cart(request):
    if request.user.is_authenticated:
        logger.debug(f"Authenticated user: {request.user}")
        cart, created = Cart.objects.get_or_create(user=request.user)
        logger.debug(f"User cart found or created: {cart.id} ")

        session_key = request.session.session_key
        if session_key:
            logger.debug(f"Session key: {session_key}")
            try:
                guest_cart = Cart.objects.get(session_key=session_key)
                logger.debug(f"Guest cart found: {guest_cart.id}")

                if guest_cart and guest_cart.items.exists():
                    for item in guest_cart.items.all():
                        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                        if not created:
                            cart_item.quantity += item.quantity
                            cart_item.save()
                        logger.debug(f"Added item {item.product.name} (Quantity: {item.quantity}) to user cart")

                    guest_cart.delete()
                    logger.debug("Guest cart deleted after merging")
            except Cart.DoesNotExist:
                logger.debug("No guest cart found for this session")
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            logger.debug(f"New session created with key: {session_key}")
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        logger.debug(f"Guest cart found or created: {cart.id} (Created: {created})")

    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key or request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        cart_item.quantity = 1
    else:
        cart_item.quantity += 1
    cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Товар добавлен в корзину.')
    return redirect('cart_detail')

def cart_detail(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    total = sum(item.quantity * item.product.price for item in cart_items)
    return render(request, 'orders/cart_detail.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, product_id):
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = get_cart(request)
    cart_items = cart.items.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            logger.debug("User not authenticated, saving cart items in session")
            request.session['cart_items'] = [{'product_id': item.product.id, 'quantity': item.quantity} for item in cart_items]
            logger.debug(f"Cart items saved in session: {request.session['cart_items']}")
            messages.info(request, 'Для оформления заказа необходимо авторизоваться.')
            return redirect(f'{reverse("login")}?next={reverse("checkout")}')

        if 'cart_items' in request.session:
            logger.debug(f"Restoring cart items from session: {request.session['cart_items']}")
            for item in request.session['cart_items']:
                product = get_object_or_404(Product, id=item['product_id'])
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                cart_item.quantity = item['quantity']
                cart_item.save()
                logger.debug(f"Restored item {product.name} to cart with quantity {cart_item.quantity}")
            del request.session['cart_items']

        delivery_address_id = request.POST.get('delivery_address')
        if not delivery_address_id:
            messages.error(request, "Пожалуйста, выберите адрес доставки.")
            return redirect('cart_detail')

        delivery_address = get_object_or_404(Address, id=delivery_address_id, user=request.user)

        order = Order.objects.create(user=request.user, delivery_address=delivery_address)
        logger.debug(f"Order created: {order.id}")
        for item in cart.items.all():
            OrderProduct.objects.create(order=order, product=item.product, quantity=item.quantity)
            logger.debug(f"Order item created: {item.product.name}, Quantity: {item.quantity}")
        cart.items.all().delete()
        logger.debug("Cart cleared after order creation")
        notify_new_order(order)
        return redirect('order_detail', pk=order.pk)

    addresses = request.user.addresses.all() if request.user.is_authenticated else []
    if not addresses.exists():
        messages.warning(request, "У вас нет доступных адресов доставки, чтобы оформить заказ, пожалуйста, добавьте адрес.")
        return redirect('add_address_page')

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total': sum(item.quantity * item.product.price for item in cart_items),
        'addresses': addresses
    })

def repeat_order(request, order_id):
    original_order = get_object_or_404(Order, id=order_id, user=request.user)
    cart, created = Cart.objects.get_or_create(user=request.user)

    for item in original_order.orderproduct_set.all():
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
        if not created:
            cart_item.quantity += item.quantity
        else:
            cart_item.quantity = item.quantity
        cart_item.save()

    return redirect('cart_detail')

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_products = OrderProduct.objects.filter(order=order)
    total = sum(item.product.price * item.quantity for item in order_products)
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'order_products': order_products,
        'total': total,
    })

def index(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user)
        session_key = None
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        carts = Cart.objects.filter(session_key=session_key)

    if carts.exists():
        cart = carts.first()
        if carts.count() > 1:
            for extra_cart in carts[1:]:
                for item in extra_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                    if not created:
                        cart_item.quantity += item.quantity
                    cart_item.save()
                extra_cart.delete()
    else:
        cart = Cart.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key
        )

    cart_product_ids = cart.items.values_list('product_id', flat=True)

    return render(request, 'orders/index.html', {
        'products': products,
        'cart_product_ids': cart_product_ids,
    })

def load_more_products(request):
    page = request.GET.get('page', 1)
    paginator = Paginator(Product.objects.all(), 20)
    products = paginator.get_page(page)

    products_list = [{
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'image': product.image.url,
        'url': reverse('product_detail', args=[product.pk])
    } for product in products]

    return JsonResponse({'products': products_list, 'has_next': products.has_next()})

def is_manager(user):
    return user.role == 'Manager' or user.role == 'Admin'

@login_required
@user_passes_test(is_manager)
def manage_products(request):
    products = Product.objects.all()
    categories = ProductCategory.objects.all()
    return render(request, 'orders/manage_products.html', {'products': products, 'categories': categories})

@login_required
@user_passes_test(is_manager)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm()
    return render(request, 'orders/add_product.html', {'form': form})

@login_required
@user_passes_test(is_manager)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'orders/edit_product.html', {'form': form})

@login_required
@user_passes_test(is_manager)
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('manage_products')

@login_required
@user_passes_test(is_manager)
def add_category(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductCategoryForm()
    return render(request, 'orders/add_category.html', {'form': form})

@login_required
@user_passes_test(is_manager)
def edit_category(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductCategoryForm(instance=category)
    return render(request, 'orders/edit_category.html', {'form': form})

@login_required
@user_passes_test(is_manager)
def delete_category(request, category_id):
    category = ProductCategory.objects.get(id=category_id)
    category.delete()
    return redirect('manage_products')

@login_required
@user_passes_test(is_manager)
def manage_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/manage_orders.html', {'orders': orders})

@login_required
@user_passes_test(is_manager)
def edit_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)  # Используем OrderForm
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус заказа обновлен.')
            return redirect('manage_orders')
    else:
        form = OrderForm(instance=order)  # Используем OrderForm
    return render(request, 'orders/edit_order_status.html', {'form': form, 'order': order})

def product_list(request):
    categories = ProductCategory.objects.all().prefetch_related('products')
    return render(request, 'orders/product_list.html', {'categories': categories})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = Review.objects.filter(product=product)
    user_review = None

    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(product=product, user=request.user)
        except Review.DoesNotExist:
            user_review = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ReviewForm(instance=user_review)

    return render(request, 'orders/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
    })

@login_required
def order_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        OrderProduct.objects.create(order=order, product=product, quantity=1)
        return redirect('order_detail', pk=order.pk)
    return render(request, 'orders/order_form.html', {'product': product})

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        review = Review.objects.get(user=request.user, product=product)
        is_editing = True
    except Review.DoesNotExist:
        review = None
        is_editing = False

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', pk=product_id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'orders/review_form.html', {
        'form': form,
        'product': product,
        'is_editing': is_editing,
    })

def categories(request):
    categories = ProductCategory.objects.all().prefetch_related('products')

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key or request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=session_key)

    cart_product_ids = cart.items.values_list('product_id', flat=True)

    return render(request, 'orders/categories.html', {
        'categories': categories,
        'cart_product_ids': cart_product_ids,
    })

def update_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

    return redirect('cart_detail')

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    for order in orders:
        total_sum = sum(item.product.price * item.quantity for item in order.orderproduct_set.all())
        order.total = total_sum
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'P':
        order.cancel()
        messages.success(request, f'Заказ {order.id} был успешно отменен.')
    else:
        messages.error(request, 'Этот заказ не может быть отменен.')
    return redirect('order_list')

def test_stars(request):
    test_ratings = [4.5, 3.3, 2.7, 5.0, 1.5]
    ratings_data = []

    for rating in test_ratings:
        width_percentage = rating * 20
        ratings_data.append({
            'rating': rating,
            'width_percentage': width_percentage,
        })

    return render(request, 'orders/test_stars.html', {'ratings_data': ratings_data})
