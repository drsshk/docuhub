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


@register.filter
def improvement_color(improvement_type):
    """Return CSS color class for improvement type"""
    color_map = {
        'feature': 'primary',
        'enhancement': 'success',
        'bugfix': 'danger',
        'security': 'warning',
        'performance': 'info',
        'ui': 'info',
        'api': 'secondary',
        'documentation': 'info',
    }
    return color_map.get(improvement_type, 'secondary')


@register.filter
def improvement_icon(improvement_type):
    """Return FontAwesome icon for improvement type"""
    icon_map = {
        'feature': 'star',
        'enhancement': 'plus-circle',
        'bugfix': 'bug',
        'security': 'shield-alt',
        'performance': 'tachometer-alt',
        'ui': 'paint-brush',
        'api': 'code',
        'documentation': 'file-alt',
    }
    return icon_map.get(improvement_type, 'circle')