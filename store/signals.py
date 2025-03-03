from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Cart, Store


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
