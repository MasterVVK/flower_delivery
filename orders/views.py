from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Review
from .forms import OrderForm, ReviewForm

def product_list(request):
    products = Product.objects.all()
    return render(request, 'orders/product_list.html', {'products': products})

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
