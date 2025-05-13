from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from django.shortcuts import get_object_or_404
from .cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem
from .models import Order
from .forms import UserEditForm, ProfileEditForm
from django.db.models import Q
from decimal import Decimal


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'main/profile.html')

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'main/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # рекомендации: товары той же категории, похожие по цене (±30%)
    recommended_products = Product.objects.filter(
        Q(category=product.category),
        ~Q(id=product.id),
        Q(price__gte=product.price * Decimal('0.7')),
        Q(price__lte=product.price * Decimal('1.3'))
    )[:4]

    return render(request, 'main/product_detail.html', {
        'product': product,
        'recommended_products': recommended_products
    })

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product=product)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'main/cart_detail.html', {'cart': cart})

@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST or None, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            return render(request, 'main/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'main/order_create.html', {'form': form, 'cart': cart})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Добавляем поле total в каждый заказ
    for order in orders:
        order.total = sum(item.get_cost() for item in order.items.all())

    return render(request, 'main/order_history.html', {'orders': orders})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'main/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def product_search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else Product.objects.none()
    return render(request, 'main/product_search.html', {'products': products, 'query': query})