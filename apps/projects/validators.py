"""
Custom validators for project models
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_project_name(value):
    """Validate project name format and content"""
    if not value or not value.strip():
        raise ValidationError(_('Project name cannot be empty.'))
    
    if len(value.strip()) < 3:
        raise ValidationError(_('Project name must be at least 3 characters long.'))
    
    if len(value) > 255:
        raise ValidationError(_('Project name cannot exceed 255 characters.'))
    
    # Check for potentially problematic characters
    


def validate_drawing_number(value):
    """Validate drawing number format"""
    if not value:
        raise ValidationError(_('Drawing number is required.'))
    
    # Must be exactly 4 alphanumeric characters
    if not re.match(r'^[A-Za-z0-9]{4}$', value):
        raise ValidationError(
            _('Drawing number must be exactly 4 alphanumeric characters (e.g., A001, M001).')
        )
    
    # Convert to uppercase for consistency
    return value.upper()


def validate_drawing_title(value):
    """Validate drawing title"""
    if value and len(value.strip()) < 2:
        raise ValidationError(_('Drawing title must be at least 2 characters long if provided.'))
    
    if value and len(value) > 255:
        raise ValidationError(_('Drawing title cannot exceed 255 characters.'))


def validate_url_format(value):
    """Validate URL format for drawing links"""
    if not value:
        return  # Optional field
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(value):
        raise ValidationError(_('Please enter a valid URL starting with http:// or https://.'))


def validate_revision_number(value):
    """Validate revision number"""
    if value < 0:
        raise ValidationError(_('Revision number cannot be negative.'))
    
    if value > 999:
        raise ValidationError(_('Revision number cannot exceed 999.'))


def validate_sort_order(value):
    """Validate sort order"""
    if value < 0:
        raise ValidationError(_('Sort order cannot be negative.'))


def validate_project_description(value):
    """Validate project description"""
    if value and len(value) > 2000:
        raise ValidationError(_('Project description cannot exceed 2000 characters.'))
    
    


def validate_version_number(value):
    """Validate project version number"""
    if value < 1:
        raise ValidationError(_('Version number must be at least 1.'))
    
    if value > 999:
        raise ValidationError(_('Version number cannot exceed 999.'))


def validate_scale_ratio(value):
    """Validate scale ratio format"""
    if not value:
        return  # Optional field
    
    # Common scale formats: 1:100, 1/100, 1-100
    scale_pattern = re.compile(r'^1[:/-]\d+$')
    if not scale_pattern.match(value):
        raise ValidationError(_('Scale ratio must be in format 1:100, 1/100, or 1-100.'))


def validate_sheet_size(value):
    """Validate sheet size format"""
    if not value:
        return  # Optional field
    
    # Common sheet sizes
    valid_sizes = ['A0', 'A1', 'A2', 'A3', 'A4', 'B0', 'B1', 'B2', 'B3', 'B4', 'C', 'D', 'E']
    if value.upper() not in valid_sizes:
        raise ValidationError(
            _('Invalid sheet size. Valid sizes: %(sizes)s') % {'sizes': ', '.join(valid_sizes)}
        )


def validate_drawing_type(value):
    """Validate drawing type"""
    if not value:
        return  # Optional field
    
    if len(value) > 50:
        raise ValidationError(_('Drawing type cannot exceed 50 characters.'))
    
    # Only allow alphanumeric, spaces, hyphens, and underscores
    if not re.match(r'^[A-Za-z0-9\s\-_]+$', value):
        raise ValidationError(_('Drawing type contains invalid characters.'))


def validate_employee_id_format(value):
    """Validate employee ID format"""
    if not value:
        return  # Optional field
    
    # Must be 3-10 alphanumeric characters
    if not re.match(r'^[A-Za-z0-9]{3,10}$', value):
        raise ValidationError(
            _('Employee ID must be 3-10 alphanumeric characters.')
        )


def validate_phone_number_format(value):
    """Validate phone number format"""
    if not value:
        return  # Optional field
    
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'[^\d]', '', value)
    
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValidationError(_('Phone number must contain 7-15 digits.'))
    
    # Basic international format validation
    phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
    if not re.match(phone_pattern, value):
        raise ValidationError(_('Please enter a valid phone number.'))


def validate_comments_length(value):
    """Validate comments field length"""
    if value and len(value) > 1000:
        raise ValidationError(_('Comments cannot exceed 1000 characters.'))


def validate_no_malicious_content(value):
    """Validate that input doesn't contain malicious content after form sanitization"""
    if not value:
        return  # Optional field
    
    # Since form sanitization with bleach.clean() happens first, this validator
    # should only catch content that somehow bypassed sanitization
    # Check for remaining dangerous patterns that could indicate sanitization bypass
    dangerous_patterns = [
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'on\w+\s*=',  # onclick, onload, etc.
    ]
    
    value_lower = value.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            raise ValidationError(_('Content contains potentially malicious code.'))


