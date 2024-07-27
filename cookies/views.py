from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from cookies.forms import CookiesForm


def reset(request: HttpRequest):
    if request.method == "POST":
        request.session.pop("cookie_consent")
    return redirect("/")


def update(request: HttpRequest):
    if request.method == "POST":
        form = CookiesForm(request.POST)
        action = request.POST.get("action")
        js = request.POST.get("js")
        if action == "accept":
            # set everything to True
            form.data = {name: True for name in form.fields}
        elif action == "decline":
            # set the required fields to True, the others to False
            form.data = {name: field.required for name, field in form.fields.items()}
        else:
            # set the required fields to True, don't change the others
            form.data = {**form.data, **{name: True for name, field in form.fields.items() if field.required}}

        if form.is_valid():
            request.session["cookie_consent"] = form.cleaned_data
            if js:
                return JsonResponse({"ok": True})
            else:
                return redirect("/")
        else:
            if js:
                return JsonResponse({"error": _("Submitted data is invalid")})
            else:
                request._cookies_form = form  # type: ignore
                return render(request, "website/site_base.html")
    else:
        return redirect("/")
