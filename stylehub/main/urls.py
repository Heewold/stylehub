from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('order/create/', views.order_create, name='order_create'),
    path('orders/', views.order_history, name='order_history'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.product_search, name='product_search'),
    path('cart/ajax/add/<int:product_id>/', views.ajax_cart_add, name='ajax_cart_add'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('order/success/', views.order_success, name='order_success'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
]
