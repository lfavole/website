from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from website.utils.paginator import paginate

from .forms import ErrorForm
from .models import Error


def display_error(_request, pk: int):
    """
    Display an error.
    """
    error = get_object_or_404(Error, pk=pk)
    return HttpResponse(error.content)


def errors_list(request: HttpRequest):
    """
    Show the list of all errors.
    """
    id_str: str | None = request.GET.get("id")
    if id_str is not None:
        try:
            id = int(id_str)
        except ValueError:
            messages.add_message(request, messages.WARNING, _("'%s' is not a valid error ID.") % id_str)
            return redirect("errors:errors_list")

        if Error.objects.filter(pk=id).exists():
            messages.add_message(request, messages.WARNING, _("The error with ID %d doesn't exist.") % id)
            return redirect("errors:error", id)
        return redirect("errors:errors_list")

    return render(
        request,
        "errors/errors_list.html",
        {
            "form": ErrorForm(),
            "page_obj": paginate(request, Error),
        },
    )
