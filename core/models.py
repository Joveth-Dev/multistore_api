from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .validators import validate_age


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
    )
    email = models.EmailField(unique=True)
    birth_date = models.DateField(validators=[validate_age], null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.get_full_name()
