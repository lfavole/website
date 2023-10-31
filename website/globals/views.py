from typing import Type

import requests
from django.conf import settings
from django.core.cache import cache
from django.db.models import Model
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.timezone import now
from django.views import generic
from globals.google_drive import FOLDER_MIMETYPE, get_google_drive_token, google_drive_files, populate_file_list  # noqa

from website.utils.http import encode_filename
from website.utils.permission import has_permission_for_view

from .models import Page, Setting


def google_drive(request, path: str):
    token = get_google_drive_token(request)
    auth_header = {"Authorization": f"Bearer {token.token}"}

    parts = path.rstrip("/").split("/")
    if parts == [""]:
        parts = []

    global google_drive_files
    google_drive_files = cache.get("google_drive_files") or google_drive_files

    ok_parts = []
    file_tree: dict | tuple[dict, dict] = google_drive_files
    file_el = {}
    while parts:
        file_id = file_el.get("id", "root")
        try:
            populate_file_list(request, file_id, ok_parts)
        except KeyError:
            raise Http404
        el = parts.pop(0)
        ok_parts.append(el)
        if el in file_tree[0]:  # it's a folder
            # must be done before (file_tree changes)
            file_el = file_tree[1][el]  # should exist
            file_tree = file_tree[0][el]
            continue
        if el in file_tree[1]:
            file_tree = file_tree[1][el]
            if parts:
                # a file was reached but there are still path components
                raise Http404
            break
        # doesn't exist
        raise Http404

    if isinstance(file_tree, tuple):  # is it a directory?
        file_id = file_el.get("id", "root")
        try:
            populate_file_list(request, file_id, ok_parts)
        except KeyError:
            raise Http404

    cache.set("google_drive_files", google_drive_files)

    if isinstance(file_tree, tuple):  # is it a directory?
        if settings.APPEND_SLASH and path and not path.endswith("/"):
            return HttpResponsePermanentRedirect(reverse("google_drive", kwargs={"path": path + "/"}))
        return render(
            request,
            "google_drive/directory_index.html",
            {
                "directory": "/" + path,
                "files": file_tree,
                "FOLDER_MIMETYPE": FOLDER_MIMETYPE,
            },
        )

    response = HttpResponse()
    response["Content-Type"] = (
        file_tree.get("mimeType", "application/octet-stream") + "; " + encode_filename(file_tree.get("name", ""))
    )
    req = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_tree.get('id', '')}",
        {"alt": "media"},
        headers=auth_header,
        stream=True,
    )
    response.content = req.iter_content(65536)
    return response


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
