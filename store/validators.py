from datetime import date

from django.core.exceptions import ValidationError


def validate_mobile_number(phone: str):
    if not phone.isdigit():
        raise ValidationError("Phone number must contain only digits.")


def validate_file_size(file):
    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("File size must not exceed 5MB.")
