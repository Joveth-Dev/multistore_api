from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Cart, Order, Store


@receiver(post_save, sender=get_user_model())
def create_cart_for_new_user(sender, instance, created, **kwargs):
    """
    Create a Cart for newly created user.
    """
    if created:
        Cart.objects.create(user=instance)


@receiver(post_save, sender=Store)
def add_user_to_store_owner(sender, instance: Store, created, **kwargs):
    """
    Add the user to the "Store Owner" group after their store is created.
    """
    if created:
        store_owner = Group.objects.get(name="Store Owner")
        instance.user.groups.add(store_owner)


@receiver(post_delete, sender=Store)
def remove_user_to_store_owner(sender, instance: Store, **kwargs):
    """
    Remove the user from the "Store Owner" group after their store is deleted.
    """
    try:
        store_owner = Group.objects.get(name="Store Owner")
        instance.user.groups.remove(store_owner)
    except Group.DoesNotExist:
        pass


@receiver(post_save, sender=Order)
def send_email_on_order_update(sender, instance: Order, created, **kwargs):
    """
    Send email to user each time their order updates to a particular status.
    """
    if not created:
        if instance.status in [
            Order.ACCEPTED,
            Order.REJECTED,
            Order.OUT_FOR_DELIVERY,
            Order.READY_FOR_PICK_UP,
            Order.COMPLETED,
        ]:
            # Customize the message based on the order status
            if instance.status == Order.ACCEPTED:
                status_message = "We're happy to inform you that your order has been accepted and is being processed."
            elif instance.status == Order.REJECTED:
                status_message = f"Unfortunately, your order has been rejected. Please contact reach out to {instance.store.name} any questions."
            elif instance.status == Order.OUT_FOR_DELIVERY:
                status_message = "Good news! Your order is out for delivery and will be with you soon."
            elif instance.status == Order.READY_FOR_PICK_UP:
                status_message = "Your order is ready for pick-up! Please collect it at your specified pick-up schedule."
            elif instance.status == Order.COMPLETED:
                status_message = "Your order has been successfully completed. We hope you enjoy your meal!"

            send_mail(
                subject=f"Order {instance.status} on FoodVille",
                message=f"""Hello {instance.cart.user.first_name}!

{status_message}

Order Details:
- Order ID: #{instance.pk}
- Status: {instance.status}
- Total Amount: ₱{instance.total_price}

Thank you for choosing FoodVille! If you have any questions or need assistance, feel free to reach out to us.

Best regards,
The FoodVille Team""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.cart.user.email],
            )
