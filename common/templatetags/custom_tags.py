from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()

    for key, value in kwargs.items():
        if (value is not None):
            query[key] = value

    return query.urlencode()


@register.filter
def get_elided_page_range(page_obj, on_each_side):
    paginator = page_obj.paginator
    current_page_number = page_obj.number

    return paginator.get_elided_page_range(
        number=current_page_number,
        on_each_side=on_each_side
    )
