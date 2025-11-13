from typing import Any

from django.core.cache import cache

CACHE_TTL = 60 * 60 * 24


def update_best_members() -> list[dict[str, Any]]:
    best_members = sorted(MOCK_USERS.values(), key=lambda user: user["rating"], reverse=True)[:5]
    cache.set("best_members", best_members, timeout=CACHE_TTL)

    return best_members


def update_popular_tags() -> list[str]:
    popular_tags = ["MySQL", "Mail.Ru", "perl", "TechnoPark", "Firefox", "Voloshin", "django", "python"]
    cache.set("popular_tags", popular_tags, timeout=CACHE_TTL)

    return popular_tags


def get_recent_activities(user_id: int) -> list[dict[str, str]]:
    display_records = []
    user_activity_records = [
        record for record in MOCK_ACTIVITIES.values()
        if record["user_id"] == user_id
    ]

    for record in user_activity_records:
        activity_type = record["type"]
        target_id = record["target_id"]

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
