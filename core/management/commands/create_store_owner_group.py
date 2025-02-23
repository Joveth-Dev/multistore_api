from django.apps import apps
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Checks if the 'Store' model exists and creates a 'Store Owner' group if it does."

    def handle(self, *args, **options):
        # Check if the 'Store' model exists
        if apps.is_installed("store"):
            if apps.get_model("store", "Store", require_ready=False):
                group, created = Group.objects.get_or_create(name="Store Owner")
                if created:
                    self.stdout.write(self.style.SUCCESS("Successfully created 'Store Owner' group."))
                else:
                    self.stdout.write(self.style.WARNING("'Store Owner' group already exists."))
            else:
                self.stdout.write(self.style.ERROR("Model 'Store' does not exist in 'store'."))
        else:
            self.stdout.write(self.style.ERROR("App 'store' is not installed."))
