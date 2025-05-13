from django import template

register = template.Library()

@register.filter
def nice_price(value):
    """
    Фильтр для красивого форматирования цены:
    - Разделяет тысячи пробелами
    - Убирает лишние нули после запятой
    - Добавляет знак ₽
    """
    try:
        value = float(value)
        # Форматируем число с двумя знаками после запятой
        formatted = f"{value:,.2f}".replace(",", " ").rstrip('0').rstrip('.')
        return f"{formatted} ₽"
    except (ValueError, TypeError):
        return value
