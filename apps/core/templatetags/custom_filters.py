from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another substring.
    Usage: {{ value|replace:"old,new" }}
    """
    if isinstance(value, str) and isinstance(arg, str):
        try:
            old, new = arg.split(',', 1)
            return value.replace(old, new)
        except ValueError:
            return value  # Return original value if arg is not in 'old,new' format
    return value