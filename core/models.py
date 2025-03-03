from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .validators import validate_age


def validate_mobile_number(phone: str):
    if not phone.isdigit():
        raise ValidationError("Phone number must contain only digits.")


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    birth_date = models.DateField(validators=[validate_age])
    address = models.TextField()
    mobile_number = models.CharField(
        max_length=11, validators=[MinLengthValidator(11), validate_mobile_number]
    )

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name()
