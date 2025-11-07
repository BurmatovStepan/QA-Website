from typing import Any

from django.core.cache import cache

MOCK_USERS = []
MOCK_ACTIVITIES = []
for i in range(1, 101):
    MOCK_USERS.append({
        "id": i,
        "login": f"[{i}] idk",
        "password": f"[{i}] still no clue",
        "email": f"[{i}] whydidi@add.this",
        "displayed_name": f"[{i}] Remembered",
        "avatar": "assets/avatar.svg" if i % 2 else "assets/better-avatar.jpeg",
        "rating": i,
        "total_questions_asked": i,
        "total_answers_posted": i,
        "disliked_questions": [i + j for j in range(5)],
    })

    MOCK_ACTIVITIES.append({
        "id": i + 101,
        "user_id": 1,
        "type": i % 3 + 1,
        "target_id": i,
        "date": "5-11-2025",
    })


CACHE_TTL = 60 * 60 * 24

def get_author_info(author_id: int) -> dict[str, Any]:
    return next(
        (user for user in MOCK_USERS if user.get("id") == author_id),
        {}
    )


def update_best_members() -> list[dict[str, Any]]:
    best_members = sorted(MOCK_USERS, key=lambda user: user.get("rating"), reverse=True)[:5]
    cache.set("best_members", best_members, timeout=CACHE_TTL)

    return best_members


def update_popular_tags() -> list[str]:
    popular_tags = ["MySQL", "Mail.Ru", "perl", "TechnoPark", "Firefox", "Voloshin", "django", "python"]
    cache.set("popular_tags", popular_tags, timeout=CACHE_TTL)

    return popular_tags


def get_recent_activities(user_id: int) -> list[dict[str, str]]:
    display_records = []
    user_activity_records = [
        record for record in MOCK_ACTIVITIES
        if record.get("user_id") == user_id
    ]

    for record in user_activity_records:
        activity_type = record.get("type")
        target_id = record.get("target_id")

        description = ""
        target_url = "#"

        match activity_type:
            case 1:
                # question_title =
                # target_url =
                description = f"Created question ..."

            case 2:
                # answer_snippet =
                # target_url =
                description = f"Liked ..."

            case 3:
                # target_url =
                description = "Changed avatar"

        display_records.append({
            "link_url": target_url,
            "description": description
        })

    return display_records

def safe_int_conversion(value: str):
    try: return int(value)
    except (ValueError, TypeError): return None
