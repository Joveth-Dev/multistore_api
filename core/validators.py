from datetime import date

from django.core.exceptions import ValidationError


def validate_age(birth_date):
    today = date.today()
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    if age < 13:
        raise ValidationError("You must be at least 13 years old to register.")
