from django import template
import os

register = template.Library()


@register.filter
def mul(value, arg):
    """Multipliziert zwei Werte"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def is_admin(user):
    """Filter - prüft ob Benutzer Admin oder Superuser ist"""
    if not user.is_authenticated:
        return False
    # Sowohl Admins (is_staff) als auch Superuser (is_superuser) dürfen den Shop verwalten
    return user.is_staff or user.is_superuser
