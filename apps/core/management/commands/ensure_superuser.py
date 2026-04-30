import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update admin user from arguments or environment variables"

    def add_arguments(self, parser):
        parser.add_argument("--from-env", action="store_true", help="Read credentials from environment")
        parser.add_argument("--username", default=None)
        parser.add_argument("--email", default=None)
        parser.add_argument("--password", default=None)

    def handle(self, *args, **options):
        from_env = options["from_env"]

        username = options["username"]
        email = options["email"]
        password = options["password"]

        if from_env:
            username = username or os.getenv("DJANGO_SUPERUSER_USERNAME")
            email = email or os.getenv("DJANGO_SUPERUSER_EMAIL")
            password = password or os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            raise CommandError("username, email and password are required")

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated superuser '{username}'"))
