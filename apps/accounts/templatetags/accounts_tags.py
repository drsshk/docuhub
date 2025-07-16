from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """
    Checks if a user has a specific role.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role.name == role_name
    except AttributeError:
        return False
