from django.views.generic import TemplateView

from common.mixins import BaseContextViewMixin


class Error404View(BaseContextViewMixin, TemplateView):
    template_name = "404.html"
    page_title = "[404] Page Not Found"


class Error401View(BaseContextViewMixin, TemplateView):
    template_name = "401.html"
    page_title = "[401] Unauthorized"
