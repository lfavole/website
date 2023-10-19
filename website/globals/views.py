from django.shortcuts import get_object_or_404, render

from .models import Setting


def home(request):
    return render(request, "home/home.html", {
        "app": "home",
        "home": get_object_or_404(Setting, slug="home"),
    })
