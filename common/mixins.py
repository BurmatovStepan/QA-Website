from typing import Any

MOCK_USERS = []
for i in range(1, 101):
    MOCK_USERS.append({
        "id": i,
        "login": "idk",
        "password": "still no clue",
        "email": "whydidi@add.this",
        "displayed_name": "Remembered",
        "avatar": "assets/avatar.svg",
        "rating": i,
        "total_questions_asked": i,
        "total_answers_posted": i,
        "disliked_questions": [i + j for j in range(5)],
    })


class BaseContextViewMixin:
    page_title = None
    main_title = None
    main_title_extra = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs) # type: ignore

        context["page_title"] = self.page_title or "Default Page Name"
        context["main_title"] = self.main_title
        context["main_title_extra"] = self.main_title_extra

        user_id = self.request.GET.get("user", None) # type: ignore
        user_id = safe_int_conversion(user_id)

        if (user_id is not None):
            context["current_user_data"] = next(
                (user for user in MOCK_USERS if user.get("id") == user_id),
                None
            )
        return context

def safe_int_conversion(value: str):
    try: return int(value)
    except (ValueError, TypeError): return None
