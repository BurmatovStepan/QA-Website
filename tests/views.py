from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render


def test_404(request: HttpRequest) -> HttpResponse:
    return render(request, "404.html")
