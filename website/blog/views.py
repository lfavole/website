from django.views import generic
from globals.views import BasePageView

from .models import Page


class PageListView(BasePageView, generic.ListView):
    """
    View for the pages list.
    """

    model = Page
    context_object_name = "pages"
    template_name = "blog/pages.html"


class PageView(BasePageView, generic.DetailView):
    """
    View for a page.
    """

    model = Page
    context_object_name = "page"
    template_name = "blog/page.html"
