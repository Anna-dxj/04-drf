from django.core.exceptions import ValidationError

def validate_number(value):
    if not value.isdigit():
        raise ValidationError('Card number must be numeric')

def validate_expiration_month(value):
    val = int(value)
    if val > 12 or val < 0:
        raise ValidationError('Must be a valid month (01~12)')
    