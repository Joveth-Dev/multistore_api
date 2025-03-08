from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Avg
from django.db.models.functions import Lower

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
    address = models.OneToOneField(Address, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
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
    is_live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.address.city}"

    def delete(self, *args, **kwargs):
        if self.image and self.image.name != "store/store/images/default.jpg":
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

    def get_display_name(self):
        if self.address and hasattr(self.address, "city"):
            return f"{self.name} - {self.address.city}"
        return str(self)

    class Meta:
        ordering = ["-updated_at", "-created_at"]


class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.store.name}"

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["-updated_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "store", name="unique_store_category_case_insensitive"
            )
        ]


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    image = models.ImageField(
        upload_to="store/product/images",
        default="store/product/images/default.jpg",
        validators=[validate_file_size],
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.image and self.image.name != "store/product/images/default.jpg":
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "store", name="unique_store_product_case_insensitive"
            )
        ]


class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{str(self.user)}'s Cart"

    class Meta:
        ordering = ["-updated_at", "-created_at"]


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, limit_choices_to={"is_available": True}
    )
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        constraints = [
            models.UniqueConstraint("cart", "product", name="unique_cart_product")
        ]


class Order(models.Model):
    NEW = "New"
    ACCEPTED = "Accepted"
    PREPARING_ORDER = "Preparing Order"
    OUT_FOR_DELIVERY = "Out For Delivery"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    STATUS_CHOICES = [
        (NEW, "New"),
        (ACCEPTED, "Accepted"),
        (PREPARING_ORDER, "Preparing Order"),
        (OUT_FOR_DELIVERY, "Out For Delivery"),
        (COMPLETED, "Completed"),
        (REJECTED, "Rejected"),
    ]
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.pk} - {self.cart.user} - {self.status}"

    class Meta:
        ordering = ["-updated_at", "-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"

    class Meta:
        ordering = ["order"]


class Feedback(models.Model):
    customer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        limit_choices_to={"status": "Completed"},
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.rating)

    class Meta:
        ordering = ["-updated_at", "-created_at"]
