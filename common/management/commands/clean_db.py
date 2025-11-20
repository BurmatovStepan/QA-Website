from time import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from qa.models import Answer, Question, Tag, Vote
from users.models import Activity, CustomUser, UserProfile

# TODO Add partial deletion

class Command(BaseCommand):
    help = "Wipes all content data from the database, leaving one specified user."

    def add_arguments(self, parser):
        parser.add_argument(
            "login",
            type=str,
            help="The login of the User to keep in the database.",
        )

        parser.add_argument(
            "--skip-confirm",
            action="store_true",
            default=False,
            help="Skip confirmation prompt.",
        )

    def handle(self, *args, **options):
        user_login = options["login"]
        skip_confirm = options["skip_confirm"]

        MODEL_EXECUTION_ORDER = [
            Activity,
            Vote,
            Answer,
            Question.tags.through,
            Question,
            Tag,
        ]

        if not skip_confirm:
            self.stdout.write(self.style.WARNING("DANGER: This will delete ALL data in the database except one user."))

            confirm = input(f"Are you sure you want to DELETE ALL DATA except for '{user_login}'? (yes/no): ")

            if confirm.lower() != "yes":
                self.stdout.write("Operation cancelled.")
                return

        start_time = time()

        try:
            user_to_keep = CustomUser.objects.get(login=user_login)

            with transaction.atomic():
                self.stdout.write(self.style.NOTICE("--- Wiping Content Models ---"))

                for Model in MODEL_EXECUTION_ORDER:
                    count, _ = Model.objects.all().delete()
                    self.stdout.write(f"  -> Deleted {count:,} records from {self.style.SQL_TABLE(Model.__name__)}.")

                self.stdout.write(self.style.NOTICE(f"\n--- Wiping Users and Profiles ---"))

                profile_count, _ = UserProfile.objects.exclude(user=user_to_keep).delete()
                self.stdout.write(f"  -> Deleted {profile_count:,} {self.style.SQL_TABLE("User Profiles")}.")

                user_count, _ =  CustomUser.objects.exclude(id=user_to_keep.id).delete()
                self.stdout.write(f"  -> Deleted {user_count:,} {self.style.SQL_TABLE("Users")}.")

                self.stdout.write(self.style.SUCCESS(f"Kept user: {user_to_keep.login} (ID: {user_to_keep.id})"))

            self.stdout.write(self.style.SUCCESS(f"\nCleanup complete in {time() - start_time:.2f}s."))

        except CustomUser.DoesNotExist:
            raise CommandError(f"User with login {user_login} not found.")

        except Exception as e:
            raise CommandError(f"Database cleanup failed: {e}")
