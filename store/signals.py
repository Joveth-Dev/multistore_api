from django.contrib.auth.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Store


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
