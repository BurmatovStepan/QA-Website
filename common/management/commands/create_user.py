from django.core.management.base import BaseCommand, CommandError

from users.models import CustomUser


class Command(BaseCommand):
    help = "Creates a normal user with the specified login, email, and password."

    def add_arguments(self, parser):
        parser.add_argument("login", type=str, help="The desired login for the new user.")
        parser.add_argument("email", type=str, help="The email address for the new user.")
        parser.add_argument("password", type=str, help="The password for the new user.")

        parser.add_argument(
            "--display-name",
            type=str,
            default=None,
            help="Optional: Display name for the user."
        )

    def handle(self, *args, **options):
        login = options["login"]
        email = options["email"]
        password = options["password"]
        display_name = options["display_name"]

        if CustomUser.objects.filter(login__iexact=login).exists():
             raise CommandError(f"User with login '{login}' already exists (case-insensitive).")

        if CustomUser.objects.filter(email__iexact=email).exists():
             raise CommandError(f"User with email '{email}' already exists (case-insensitive).")

        try:
            user = CustomUser.objects.create_user(
                login=login,
                email=email,
                password=password,
                display_name=display_name
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully created normal user: {user.login}")
            )
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"Is Staff: {user.is_staff}")

        except ValueError as e:
            raise CommandError(f"User creation failed: {e}")
