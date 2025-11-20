from math import inf
from random import choice, randint, sample
from time import time

import inflect
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.utils.text import slugify
from faker import Faker

from qa.models import Answer, Question, Tag, Vote
from users.models import Activity, CustomUser, UserProfile

# TODO Add support for appending data
# TODO Create script that recalculates rating based on DB
# TODO Disable some users

BATCH_SIZE = 10_000
DEFAULT_PASSWORD = "qwerty"

INFLECT_ENGINE = inflect.engine()

MODEL_EXECUTION_ORDER = ["user", "user_profile", "tag", "question", "answer", "vote", "activity"]
MODEL_MULTIPLIERS = {
    "user": 1,
    "user_profile": 1,
    "tag": 1,
    "question": 10,
    "answer": 100,
    "vote": 200,
    "activity": 200,
}

class ProgressTracker:
    report_threshold = 0
    next_report_threshold = 0
    entities_created = 0
    entities_created_between_thresholds = 0
    target_total = 0

    def __init__(self, report_threshold, target_total):
        self.report_threshold = report_threshold
        self.next_report_threshold = report_threshold
        self.target_total = target_total

    def create_entities(self, count):
        self.entities_created += count
        self.entities_created_between_thresholds += count

        if self.entities_created == self.target_total:
            return (self.entities_created_between_thresholds, False)

        if self.entities_created >= self.target_total:
            return (self.entities_created_between_thresholds, True)

        if self.entities_created >= self.next_report_threshold:
            self.next_report_threshold += self.report_threshold
            self.entities_created_between_thresholds = 0
            return (self.entities_created, True)

        return (None, False)


class Command(BaseCommand):
    help = "Fills the database with test data: users, questions, answers, tags, and votes."

    def add_arguments(self, parser):
        parser.add_argument(
            "ratio",
            type=int,
            help="Coefficient (ratio) for filling entities. e.g., 10000 for 10k users.",
        )

        parser.add_argument(
            "--models",
            nargs="+",
            help="Models for which data will be created.",
        )

    def handle(self, *args, **options):
        CREATION_FUNCTIONS = {
            "user": self.create_users,
            "user_profile": self.create_user_profiles,
            "tag": self.create_tags,
            "question": self.create_questions,
            "answer": self.create_answers,
            "vote": self.create_votes,
            "activity": self.create_activities,
        }

        ratio = options["ratio"]
        models = options["models"]

        if models is None:
            models = MODEL_EXECUTION_ORDER
        else:
            models = [model.lower() for model in models]

        self.stdout.write(f"--- Filling {self.style.SQL_TABLE(self.make_main_heading(models))} with ratio: {ratio} ---")

        for name in MODEL_EXECUTION_ORDER:
            if name in models:
                count = ratio * MODEL_MULTIPLIERS[name]
                creator_function = CREATION_FUNCTIONS[name]

                start_time = time()
                creator_function(count)
                self.stdout.write(self.style.SUCCESS(f"Created {count:,} {INFLECT_ENGINE.plural(name.replace("_", " "))} in {time() - start_time:.2f}s"))

    def _bulk_create_model(self, EntityModel, total, entity_name, entity_generator):
        entity_name_plural = INFLECT_ENGINE.plural(entity_name)

        self.stdout.write(f"\nCreating {total:,} {self.style.SQL_TABLE(entity_name_plural)}...")
        REPORT_THRESHOLD = max(BATCH_SIZE * 2, total // 20)

        progress_tracker = ProgressTracker(REPORT_THRESHOLD, total)

        new_entities = []

        should_optimize = False
        if EntityModel.__name__ in ["Question", "Answer"]:
            db_conn = connections[EntityModel.objects.db]
            should_optimize = True

        try:
            with transaction.atomic():
                if should_optimize:
                    with db_conn.cursor() as cursor:
                        self.stdout.write(self.style.NOTICE("  -> Disabling Foreign Key checks..."))
                        cursor.execute("SET session_replication_role = 'replica';")

                for i in range(1, total + 1):
                    entity = entity_generator(i)
                    new_entities.append(entity)

                    if len(new_entities) >= BATCH_SIZE:
                        EntityModel.objects.bulk_create(new_entities, BATCH_SIZE)
                        progress, to_print = progress_tracker.create_entities(len(new_entities))
                        new_entities = []

                        if to_print:
                            self.stdout.write(f"  -> Bulk created {progress:,} {entity_name_plural} so far...")

                if new_entities:
                    EntityModel.objects.bulk_create(new_entities, BATCH_SIZE)
                    progress, to_print = progress_tracker.create_entities(len(new_entities))

                self.stdout.write(f"  >> Bulk created final {progress:,} {entity_name_plural}.")

                if should_optimize:
                    with db_conn.cursor() as cursor:
                        self.stdout.write(self.style.NOTICE("  -> Re-enabling Foreign Key checks..."))
                        cursor.execute("SET session_replication_role = 'origin';")

        except Exception as e:
            raise CommandError(f"Database creation failed: {e}")


    def create_users(self, total):
        hashed_password = make_password(DEFAULT_PASSWORD)

        def user_generator(i):
            login = f"user_{i}"
            email = f"user_{i}@example.com"

            return CustomUser(
                login=login,
                email=email,
                password=hashed_password,
                is_active=(i % 250 != 0),
                is_staff=(i % 100 == 0),
            )

        self._bulk_create_model(
            EntityModel=CustomUser,
            total=total,
            entity_name="user",
            entity_generator=user_generator
        )

    def create_user_profiles(self, total):
        fake = Faker()

        user_ids = list(CustomUser.objects.filter(profile__isnull=True).values_list("id", flat=True))

        if len(user_ids) == 0:
            raise CommandError("No users were found to link profiles.")

        def profile_generator(i):
            user_id = user_ids[i - 1]

            return UserProfile(
                user_id=user_id,
                display_name=fake.user_name(),
                rating=randint(0, 1000),
            )

        self._bulk_create_model(
            EntityModel=UserProfile,
            total=total,
            entity_name="user profile",
            entity_generator=profile_generator
        )


    def create_tags(self, total):
        fake = Faker()

        def tag_generator(i):
            name = f"{fake.word()} [{i}]"

            return Tag(
                name=name,
                slug=slugify(name),
            )

        self._bulk_create_model(
            EntityModel=Tag,
            total=total,
            entity_name="tag",
            entity_generator=tag_generator
        )

    def create_questions(self, total):
        fake = Faker()

        user_ids = list(CustomUser.objects.values_list("id", flat=True))
        tag_ids = list(Tag.objects.values_list("id", flat=True))

        if len(user_ids) == 0:
            raise CommandError("No users were found to link questions.")

        if len(tag_ids) == 0:
            raise CommandError("No tags were found to link questions.")

        def question_generator(i):
            author_id = choice(user_ids)
            title = fake.sentence(nb_words=6)
            content = fake.paragraph(nb_sentences=5)

            return Question(
                author_id=author_id,
                title=title,
                slug=slugify(title),
                rating_total=randint(-(total // 50), total // 50),
                answer_count=randint(0, 15),
                content=content,
                view_count=randint(0, total),
                is_active=(i % 100 != 0)
            )

        self._bulk_create_model(
            EntityModel=Question,
            total=total,
            entity_name="question",
            entity_generator=question_generator
        )

        REPORT_THRESHOLD = max(BATCH_SIZE * 2, (total * 3) // 20)

        question_ids = list(Question.objects.values_list("id", flat=True))
        QuestionTagModel = Question.tags.through

        new_m2m_links = []
        progress_tracker = ProgressTracker(REPORT_THRESHOLD, inf)

        try:
            with transaction.atomic():
                self.stdout.write("\n  -> Preparing M2M links for bulk creation...")

                for question_id in question_ids:
                    tag_ids_to_add = sample(tag_ids, randint(1, 5))

                    for tag_id in tag_ids_to_add:
                        link = QuestionTagModel(question_id=question_id, tag_id=tag_id)
                        new_m2m_links.append(link)

                    if len(new_m2m_links) >= BATCH_SIZE:
                        QuestionTagModel.objects.bulk_create(new_m2m_links, BATCH_SIZE)
                        progress, to_print = progress_tracker.create_entities(len(new_m2m_links))
                        new_m2m_links = []

                        if to_print:
                            self.stdout.write(f"  -> Bulk created {progress:,} M2M links so far...")

                if new_m2m_links:
                    QuestionTagModel.objects.bulk_create(new_m2m_links, BATCH_SIZE)

                progress, to_print = progress_tracker.create_entities(len(new_m2m_links))
                self.stdout.write(f"  >> Bulk created final {len(new_m2m_links):,} M2M links.")

        except Exception as e:
            raise CommandError(f"Question creation failed: {e}")

    def create_answers(self, total):
        fake = Faker()

        user_ids = list(CustomUser.objects.values_list("id", flat=True))
        question_ids = list(Question.objects.values_list("id", flat=True))

        if len(user_ids) == 0:
            raise CommandError("No users were found to link answers.")

        if len(question_ids) == 0:
            raise CommandError("No questions were found to link answers.")

        def answer_generator(i):
            question_id = choice(question_ids)
            author_id = choice(user_ids)
            content = fake.paragraph(nb_sentences=8)

            return Answer(
                question_id=question_id,
                author_id=author_id,
                rating_total=randint(-(total // 2000), total // 2000),
                content=content,
                is_correct=(i % 10 == 0),
                is_active=(i % 100 != 0)
            )
        self._bulk_create_model(
            EntityModel=Answer,
            total=total,
            entity_name="answer",
            entity_generator=answer_generator
        )

    def create_votes(self, total):
        self.stdout.write(f"\nCreating {total:,} {self.style.SQL_TABLE("votes")}...")
        REPORT_THRESHOLD = max(BATCH_SIZE * 2, total // 20)
        TARGET_OPTIONS = []

        progress_tracker = ProgressTracker(REPORT_THRESHOLD, total)

        new_votes = []
        created_vote_tuples = set()

        user_ids = CustomUser.objects.values_list("id", flat=True)
        question_ids = Question.objects.values_list("id", flat=True)
        answer_ids = Answer.objects.values_list("id", flat=True)

        if (len(question_ids) == 0 and len(answer_ids) == 0):
            raise CommandError("No questions/answers were found to link votes.")

        if len(question_ids) > 0:
            question_content_type = ContentType.objects.get_for_model(Question)
            TARGET_OPTIONS.append((question_content_type.id, question_ids))

        if len(answer_ids) > 0:
            answer_content_type = ContentType.objects.get_for_model(Answer)
            TARGET_OPTIONS.append((answer_content_type.id, answer_ids))

        db_conn = connections[Vote.objects.db]

        try:
            with transaction.atomic():
                with db_conn.cursor() as cursor:
                    self.stdout.write(self.style.NOTICE("  -> Disabling Foreign Key checks..."))
                    cursor.execute("SET session_replication_role = 'replica';")

                attempts = 0
                while len(created_vote_tuples) < total:
                    attempts += 1

                    user_id = choice(user_ids)
                    vote_type = choice(Vote.VOTE_CHOICES)
                    target_content_type_id, target_ids = choice(TARGET_OPTIONS)

                    if not target_ids:
                        continue

                    target_id = choice(target_ids)
                    vote_tuple = (user_id, target_content_type_id, target_id)

                    if vote_tuple not in created_vote_tuples:
                        created_vote_tuples.add(vote_tuple)
                        vote = Vote(
                            user_id=user_id,
                            type=vote_type[0],
                            content_type_id=target_content_type_id,
                            object_id=target_id,
                        )
                        new_votes.append(vote)

                    if len(new_votes) >= BATCH_SIZE:
                        Vote.objects.bulk_create(new_votes, BATCH_SIZE)
                        progress, to_print = progress_tracker.create_entities(len(new_votes))
                        new_votes = []

                        if to_print:
                            self.stdout.write(f"  -> Bulk created {progress:,} votes so far...")

                    if attempts % (REPORT_THRESHOLD * 5) == 0:
                        self.stdout.write(self.style.NOTICE(f"  -> Generated {len(created_vote_tuples):,} unique votes in {attempts:,} attempts..."))

                if new_votes:
                    Vote.objects.bulk_create(new_votes, BATCH_SIZE)
                    progress, to_print = progress_tracker.create_entities(len(new_votes))

                self.stdout.write(f"  >> Bulk created final {progress:,} votes.")

                with db_conn.cursor() as cursor:
                    self.stdout.write(self.style.NOTICE("  -> Re-enabling Foreign Key checks..."))
                    cursor.execute("SET session_replication_role = 'origin';")

        except Exception as e:
            raise CommandError(f"Vote creation failed: {e}")


    def create_activities(self, total):
        self.stdout.write(f"\nCreating {total:,} {self.style.SQL_TABLE("activities")}...")
        REPORT_THRESHOLD = max(BATCH_SIZE * 2, total // 20)
        TARGET_OPTIONS = []

        progress_tracker = ProgressTracker(REPORT_THRESHOLD, total)

        user_ids = list(CustomUser.objects.values_list("id", flat=True))
        question_ids = list(Question.objects.values_list("id", flat=True))
        answer_ids = list(Answer.objects.values_list("id", flat=True))

        if len(user_ids) > 0:
            user_content_type = ContentType.objects.get_for_model(CustomUser)
            TARGET_OPTIONS.append((user_content_type.id, user_ids))
        else:
            raise CommandError("No users were found to link activities.")

        if len(question_ids) > 0:
            question_content_type = ContentType.objects.get_for_model(Question)
            TARGET_OPTIONS.append((question_content_type.id, question_ids))

        if len(answer_ids) > 0:
            answer_content_type = ContentType.objects.get_for_model(Answer)
            TARGET_OPTIONS.append((answer_content_type.id, answer_ids))

        new_activities = []

        db_conn = connections[Activity.objects.db]

        try:
            with transaction.atomic():
                with db_conn.cursor() as cursor:
                    self.stdout.write(self.style.NOTICE("  -> Disabling Foreign Key checks..."))
                    cursor.execute("SET session_replication_role = 'replica';")

                for i in range(1, total + 1):
                    user_id = choice(user_ids)
                    target_content_type_id, target_ids = choice(TARGET_OPTIONS)

                    if target_content_type_id == user_content_type.id:
                        activity_type = choice(list(filter(lambda activity: activity[0].startswith("U_"), Activity.ACTIVITY_TYPES)))
                        target_id = user_id

                    elif target_content_type_id == question_content_type.id:
                        activity_type = choice(list(filter(lambda activity: activity[0].startswith("Q_"), Activity.ACTIVITY_TYPES)))
                        target_id = choice(target_ids)

                    elif target_content_type_id == answer_content_type.id:
                        activity_type = choice(list(filter(lambda activity: activity[0].startswith("A_"), Activity.ACTIVITY_TYPES)))
                        target_id = choice(target_ids)

                    activity = Activity(
                        user_id=user_id,
                        type=activity_type[0],
                        content_type_id=target_content_type_id,
                        object_id=target_id,
                    )
                    new_activities.append(activity)

                    if len(new_activities) >= BATCH_SIZE:
                        Activity.objects.bulk_create(new_activities, BATCH_SIZE)
                        progress, to_print = progress_tracker.create_entities(len(new_activities))
                        new_activities = []

                        if to_print:
                            self.stdout.write(f"  -> Bulk created {progress:,} activities so far...")

                if new_activities:
                    Activity.objects.bulk_create(new_activities, BATCH_SIZE)
                    progress, to_print = progress_tracker.create_entities(len(new_activities))

                self.stdout.write(f"  >> Bulk created final {progress:,} activities.")

                with db_conn.cursor() as cursor:
                    self.stdout.write(self.style.NOTICE("  -> Re-enabling Foreign Key checks..."))
                    cursor.execute("SET session_replication_role = 'origin';")

        except Exception as e:
            raise CommandError(f"Vote creation failed: {e}")

    def make_main_heading(self, model_names):
        result = []
        for name in model_names:
            name = [word.capitalize() for word in name.split("_")]
            name = " ".join(name)

            result.append(name)

        return ", ".join(result)
