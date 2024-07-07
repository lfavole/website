import datetime as dt

from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import TemperaturesForm
from .models import Temperature
from .templatetags.temperatures_utils import missing_extra_days


def admin(request):
    if request.method == "POST":
        form = TemperaturesForm(request.POST)
        if form.is_valid():
            form.save()
            # send the missing / extra days for AJAX requests
            if "ajax" in request.POST:
                return HttpResponse(missing_extra_days())
            # redirect to the same page
            return redirect("temperatures:home")
    else:
        initial_data = {}
        if "date" in request.GET:
            try:
                date = dt.date.fromisoformat(request.GET["date"])
            except ValueError:
                pass
            else:
                initial_data["date"] = str(date)
        form = TemperaturesForm(initial=initial_data)

    return render(request, "temperatures/admin.html", {"form": form})


def chart(request):
    return render(request, "temperatures/chart.html", {"temperatures": Temperature.objects.all()})


def home(request):
    return render(request, "temperatures/home.html")
