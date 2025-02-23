from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from .validators import validate_mobile_number


class Address(models.Model):
    city = models.CharField(max_length=30)
    province = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city}, {self.province}"

    class Meta:
        ordering = ["-updated_at", "-created_at"]


class Store(models.Model):
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="store/images", default="store/images/default.jpg"
    )
    mobile_number = models.CharField(
        max_length=11, validators=[MinLengthValidator(11), validate_mobile_number]
    )
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.opening_time == self.closing_time:
            raise ValidationError("Opening time and closing time cannot be the same.")

    def __str__(self):
        return f"{self.name} - {self.address.city}"

    class Meta:
        ordering = ["-updated_at", "-created_at"]
