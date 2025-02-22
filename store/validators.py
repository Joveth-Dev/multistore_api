from datetime import date

from django.core.exceptions import ValidationError


def validate_mobile_number(phone: str):
    if not phone.isdigit():
        raise ValidationError("Phone number must contain only digits.")