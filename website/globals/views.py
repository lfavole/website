from typing import Type

from django.db.models import Model
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.views import generic

from website.utils.permission import has_permission_for_view

from .models import Page, Setting


def home(request):
    return render(
        request,
        "home/home.html",
        {
            "app": "home",
            "home": get_object_or_404(Setting, slug="home"),
        },
    )


class BasePageView(generic.View):
    """
    Base view for a page / list of pages.
    """

    model: Type[Model]

    def get_queryset(self):  # pylint: disable=C0116
        admin = has_permission_for_view(self, "view")
        ret = self.model.objects.all()
        if not admin:
            if hasattr(self.model, "content"):
                ret = ret.filter(~Q(content__exact=""))
            if hasattr(self.model, "hidden"):
                ret = ret.filter(hidden=False)
            if hasattr(self.model, "date"):
                ret = ret.filter(date__lte=now())
        return ret


class PageView(BasePageView, generic.DetailView):
    """
    View for a page.
    """

    context_object_name = "page"
    template_name = "home/page.html"
    model = Page
