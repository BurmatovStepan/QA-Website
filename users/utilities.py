from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def get_safe_redirect_url(request):
    next_url = request.GET.get("next")
    next_url_is_safe = url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()}
    )

    if next_url_is_safe:
        return next_url
    else:
        return reverse("current_user_profile")
