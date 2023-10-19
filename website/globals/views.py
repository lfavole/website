from django.shortcuts import get_object_or_404, render

from .models import SpecialContent


def home(request):
    return render(request, "home/home.html", {
        "app": "home",
        "home": get_object_or_404(SpecialContent, slug="home"),
    })
