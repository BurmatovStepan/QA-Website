from typing import Any
from django.views.generic import TemplateView

from common.mixins import BaseContextViewMixin


class Error404View(BaseContextViewMixin, TemplateView):
    template_name = "404.html"
    page_title = "[404] Page Not Found"

