from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from .validators import validate_file_size, validate_mobile_number


class Address(models.Model):
    city = models.CharField(max_length=30)
    province = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.city}, {self.province}"

    class Meta:
        ordering = ["-updated_at", "-created_at"]


class Store(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(
        upload_to="store/store/images",
        default="store/store/images/default.jpg",
        validators=[validate_file_size],
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

    def __str__(self):
        return f"{self.name} - {self.address.city}"

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        self.address.delete()
        super().delete(*args, **kwargs)

    def clean(self):
        if self.opening_time == self.closing_time:
            raise ValidationError("Opening time and closing time cannot be the same.")

    @property
    def is_open(self):
        """Check if the store is currently open based on the opening and closing time."""
        now = datetime.now().time()

        if self.opening_time < self.closing_time:
            return (
                self.opening_time <= now < self.closing_time
            )  # Regular case (same day)
        else:
            return (
                now >= self.opening_time or now < self.closing_time
            )  # Overnight case (e.g., 10 PM to 6 AM)

    class Meta:
        ordering = ["-updated_at", "-created_at"]


class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["-updated_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["store", "name"], name="unique_store_name")
        ]


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(
        upload_to="store/product/images",
        default="store/product/default.jpg",
        validators=[validate_file_size],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-updated_at", "-created_at"]
