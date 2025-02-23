from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from core.models import User


class Command(BaseCommand):
    help = """
    Tries to create a superuser.
    """

    def handle(self, *args, **options):
        print("Creating a new superuser...")
        try:
            new_user = User.objects.create(
                email="admin@domain.com", is_staff=True, is_superuser=True
            )
            new_user.set_password("05nMub2q")
            new_user.save()
            print("New superuser created:\nemail: admin@domain.com\npassword: 05nMub2q")
        except IntegrityError as e:
            print(str(e))
