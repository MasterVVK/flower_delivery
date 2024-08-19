from django import template
import logging

register = template.Library()

@register.filter
def multiply(value, arg):
    logging.info(f"multiply filter called with {value} and {arg}")
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''
