from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Store


@receiver(post_save, sender=Store)
def my_signal_handler(sender, instance, created, **kwargs):
    if created:
        store_owner = Group.objects.get(name="Store Owner")
        instance.user.groups.add(store_owner)