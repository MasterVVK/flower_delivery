# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, ProductCategory, Order, Review
from .forms import ProductForm, ProductCategoryForm, OrderForm, ReviewForm
from django.urls import reverse  # Добавьте этот импорт
from django.core.paginator import Paginator
from django.http import JsonResponse

def index(request):
    # Получаем первые 20 товаров для начального отображения
    products = Product.objects.all()[:20]
    return render(request, 'orders/index.html', {'products': products})

def load_more_products(request):
    # Получаем номер страницы из GET-запроса
    page = request.GET.get('page', 1)
    # Создаем пагинатор с шагом 20 товаров на страницу
    paginator = Paginator(Product.objects.all(), 20)
    # Получаем товары для указанной страницы
    products = paginator.get_page(page)
    # Формируем список товаров в формате JSON
    products_list = [{
        'name': product.name,
        'price': product.price,
        'image': product.image.url,
        'url': reverse('product_detail', args=[product.pk])
    } for product in products]
    # Возвращаем JSON-ответ
    return JsonResponse({'products': products_list})

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

def product_list(request):
    categories = ProductCategory.objects.all().prefetch_related('products')
    return render(request, 'orders/product_list.html', {'categories': categories})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = Review.objects.filter(product=product)
    return render(request, 'orders/product_detail.html', {'product': product, 'reviews': reviews})

@login_required
def order_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            order.products.add(product)
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'orders/order_form.html', {'form': form, 'product': product})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', pk=product_id)
    else:
        form = ReviewForm()
    return render(request, 'orders/review_form.html', {'form': form, 'product': product})

def categories(request):
    categories = ProductCategory.objects.all().prefetch_related('products')
    return render(request, 'orders/categories.html', {'categories': categories})