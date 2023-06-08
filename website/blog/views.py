from django.contrib.auth import get_permission_codename
from django.db.models import Model
from django.db.models.query_utils import Q
from django.utils.timezone import now
from django.views import generic

from .models import Page


def has_permission(view: generic.View, permission="view"):
    model: Model = view.model  # type: ignore
    perm_name = model._meta.app_label + "." + get_permission_codename(permission, model._meta)
    return view.request.user.has_perm(perm_name)  # type: ignore


class BasePageView(generic.View):
    """
    Base view for pages (pages list or one page).
    """

    model = Page

    is_article = False

    def get_queryset(self):
        admin = has_permission(self, "view")
        ret = self.model.objects.all()
        if not admin:
            # return the pages that have content, are not hidden and not future
            ret = ret.filter(~Q(content__exact="")).filter(hidden=False).filter(date__lte=now())
        return ret


class PageListView(BasePageView, generic.ListView):
    """
    View for the pages list.
    """

    context_object_name = "pages"
    template_name = "blog/pages.html"


class PageView(BasePageView, generic.DetailView):
    """
    View for a page.
    """

    context_object_name = "page"
    template_name = "blog/page.html"
