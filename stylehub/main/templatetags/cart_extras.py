from django import template
from main.models import Product

register = template.Library()

@register.filter
def split(value, key):
    """Разделить строку по разделителю"""
    return value.split(key)

@register.filter
def get_item(products, product_id):
    """Получить товар по ID"""
    try:
        return Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return None

@register.filter
def mul(value, arg):
    """Умножить два значения"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
