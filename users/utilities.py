from django.urls import resolve, Resolver404
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpRequest
from django.urls import reverse


def get_safe_redirect_url(request: HttpRequest, next_url: str | None, fallback_page: str = "homepage") -> str:
    if next_url is None:
        return reverse(fallback_page)

    next_url_is_safe = url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    )

    if not next_url_is_safe:
        return next_url

    try:
        path = next_url.split(request.get_host(), 1)[-1]
        resolve(path)
        return next_url

    except Resolver404:
        return reverse(fallback_page)
