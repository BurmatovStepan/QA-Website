from typing import Any

from django import template
from users.models import CustomUser
from django.core.paginator import Page

# TODO Rename or split these

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context: dict[str, Any], **kwargs) -> str:
    query = context["request"].GET.copy()

    for key, value in kwargs.items():
        if value is not None:
            query[key] = value

    return query.urlencode()


@register.filter
def get_elided_page_range(page_obj: Page, on_each_side: int):
    paginator = page_obj.paginator
    current_page_number = page_obj.number

    return paginator.get_elided_page_range(
        number=current_page_number,
        on_each_side=on_each_side
    )


@register.filter
def get_display_name(user: CustomUser):
    return user.display_name if user.display_name else user.login


@register.filter
def field_type(field):
    return field.field.__class__.__name__


@register.filter
def is_disabled(field):
    return field.field.disabled


@register.filter
def is_required(field):
    return field.field.required
