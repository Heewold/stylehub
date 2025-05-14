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
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect

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
    products = Product.objects.all()
    categories = Category.objects.all()
    category = None

    # ✅ Фильтр по категории из формы
    selected_category = request.GET.get('category')
    if selected_category:
        category = get_object_or_404(Category, id=selected_category)
        products = products.filter(category=category)
    elif category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # ✅ Фильтр по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    paginator = Paginator(products, 9)  # Пагинация (9 товаров на страницу)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'selected_category': selected_category
    }
    return render(request, 'main/product_list.html', context)




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    sizes = product.get_sizes_list()

    # ✅ Похожие товары: те же категории, исключая сам товар
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'sizes': sizes,
        'cart': cart,
        'similar_products': similar_products,
    }
    return render(request, 'main/product_detail.html', context)



def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size', '')
    cart = request.session.get('cart', {})

    key = f"{product_id}:{size}"
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')


def cart_remove(request, product_id, size=''):
    cart = request.session.get('cart', {})
    key = f"{product_id}:{size}"
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    products = {}
    total = 0

    for key, quantity in cart.items():
        parts = key.split(':')
        product_id = parts[0]
        size = parts[1] if len(parts) > 1 else ''

        try:
            product = Product.objects.get(pk=product_id)
            products[key] = {
                'product': product,
                'size': size,
                'quantity': quantity,
                'total_price': product.price * quantity
            }
            total += product.price * quantity
        except Product.DoesNotExist:
            pass

    return render(request, 'main/cart_detail.html', {
        'cart_items': products,
        'total': total,
    })


@login_required
def order_create(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user    # ✅ если пользователь есть
            order.save()

            for key, quantity in cart.items():
                parts = key.split(':')
                product_id = parts[0]
                size = parts[1] if len(parts) > 1 else ''

                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=product.price,
                        quantity=quantity,
                        size=size
                    )
                except Product.DoesNotExist:
                    pass

            request.session['cart'] = {}
            return redirect('order_success')
    else:
        form = OrderCreateForm()

    return render(request, 'main/order_create.html', {'form': form})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')

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

def ajax_cart_add(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return JsonResponse({'success': True, 'cart_count': sum(cart.values())})


def cart_clear(request):
    request.session['cart'] = {}
    request.session.modified = True
    return redirect('cart_detail')

def order_success(request):
    return render(request, 'main/order_success.html')

def toggle_theme(request):
    theme = request.session.get('theme', 'light')
    request.session['theme'] = 'dark' if theme == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', '/'))
