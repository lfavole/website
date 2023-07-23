from django.db.models.query_utils import Q
from django.utils.timezone import now
from django.views import generic

from website.utils.permission import has_permission

from .models import Page


def has_permission_for_view(view: generic.View, permission="view"):
    return has_permission(view.request, view.model, permission)  # type: ignore


class BasePageView(generic.View):
    """
    Base view for pages (pages list or one page).
    """

    model = Page

    is_article = False

    def get_queryset(self):
        admin = has_permission_for_view(self, "view")
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
