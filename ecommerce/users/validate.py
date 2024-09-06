from django.core.exceptions import ValidationError

def validate_passwords_match(password, confirm_password):
        if password != confirm_password: 
            raise ValidationError('Passwords must match')