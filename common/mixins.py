from typing import Any

MOCK_QUESTIONS = []
MOCK_ANSWERS = []
MOCK_USERS = []
MOCK_ACTIVITIES = []
for i in range(1, 101):
    MOCK_QUESTIONS.append({
        "id": i,
        "author_id": i,
        "rating": i,
        "title": f"[{i}] Where do I find clothes?",
        "content": f"[{i}] So I'm at a store and I can't find them, there's only soup. I went through every aisle but there was only more soup. What do I do? This question description is significantly longer than the over one so I have to add more styles to fix that. Quick brown fox jumped over the lazy dog. I don't have lorem ipsum copypasta. Remebered that br exists.",
        "tags": [f"[{i}] soup", f"[{i}] tf2"],
        "answer_amount": i,
        "creation_date": "5-11-2025",
        "is_hot": i % 2,
    })

    MOCK_ANSWERS.append({
        "id": i,
        "question_id": i,
        "author_id": i,
        "rating": i,
        "content": f"[{i}] I've never had a similar experience so I consider myself an expert is this field, so I think you should buy some soup.",
        "is_correct": i % 2,
    })

    MOCK_ANSWERS.append({
        "id": i + 100,
        "question_id": 1,
        "author_id": 1,
        "rating": i + 100,
        "content": f"[{i + 100}] I've never had a similar experience so I consider myself an expert is this field, so I think you should buy some soup.",
        "is_correct": i % 10 == 0,
    })

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
        "id": i,
        "user_id": i,
        "type": i % 3 + 1,
        "target_id": i,
        "date": "5-11-2025",
    })

    MOCK_ACTIVITIES.append({
        "id": i + 101,
        "user_id": 1,
        "type": i % 3 + 1,
        "target_id": i,
        "date": "5-11-2025",
    })

class BaseContextViewMixin:
    page_title = None
    main_title = None
    main_title_extra = None

    #! REMOVE LATER
    current_user = None
    items_per_page = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs) # type: ignore

        context["page_title"] = self.page_title or "Default Page Name"
        context["main_title"] = self.main_title
        context["main_title_extra"] = self.main_title_extra

        context["current_user"] = self.current_user

        return context

    def dispatch(self, request, *args, **kwargs):
        user_id = self.request.GET.get("user", None) # type: ignore
        user_id = safe_int_conversion(user_id)

        if (user_id is not None):
            self.current_user = next(
                (user for user in MOCK_USERS if user.get("id") == user_id),
                None
            )

        page_size = self.request.GET.get("page-size", None) # type: ignore
        self.items_per_page = safe_int_conversion(page_size)

        return super().dispatch(request, *args, **kwargs) # type: ignore

def safe_int_conversion(value: str):
    try: return int(value)
    except (ValueError, TypeError): return None
