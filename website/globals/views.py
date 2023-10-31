import datetime as dt
from pathlib import PurePosixPath
from typing import Type

import requests
from django.conf import settings
from django.core.cache import cache
from django.db.models import Model
from django.db.models.query_utils import Q
from django.http import Http404, HttpRequest, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now, get_default_timezone
from django.views import generic
from globals.google_drive import FOLDER_MIMETYPE, get_google_drive_token, google_drive_files, populate_file_list  # noqa

import custom_settings
from website.utils.http import encode_filename
from website.utils.permission import has_permission_for_view

from .forms import ContactCaptchaForm
from .models import Page, Setting

CAPTCHA_EXPIRE_DURATION = dt.timedelta(seconds=3600)
CAPTCHA_KEY = "contact_last_captcha_time"


def _captcha_expired(request):
    last_check_time = request.session.get(CAPTCHA_KEY)
    if not last_check_time:
        return True
    last_check_time = dt.datetime.fromisoformat(last_check_time)
    return last_check_time + CAPTCHA_EXPIRE_DURATION < now()


def contact_captcha(request: HttpRequest):
    if not _captcha_expired(request):
        return redirect("contact")

    if request.method == "POST":
        form = ContactCaptchaForm(request.POST)
        if form.is_valid():
            request.session[CAPTCHA_KEY] = str(now())
            return redirect("contact")
    else:
        form = ContactCaptchaForm()
    return render(request, "home/contact_captcha.html", {"form": form})


def contact(request):
    if _captcha_expired(request):
        return redirect("contact_captcha")

    return render(
        request,
        "home/contact.html",
        {
            "app": "home",
            "contact": get_object_or_404(Setting, slug="contact"),
        },
    )


def google_drive(request: HttpRequest, path: str):
    if request.user.username == custom_settings.ADMIN_NAME:  # type: ignore
        folders = [""]
    else:
        folders = custom_settings.GOOGLE_DRIVE_FOLDERS
    token = get_google_drive_token(request)
    auth_header = {"Authorization": f"Bearer {token.token}"}

    parts = path.rstrip("/").split("/")
    if parts == [""]:
        parts = []

    path_obj = PurePosixPath(path)
    rem_parts_0 = []
    ok = False
    ok_all = False
    for folder in folders:
        path_to_check = PurePosixPath(folder)
        parents_and_self = [path_to_check, *path_to_check.parents]
        if path_to_check in [path_obj, *path_obj.parents]:
            # it's a child of an authorized folder => show all files, stop everything
            ok_all = True
            ok = True
            break
        prev_parent = None
        for parent in parents_and_self:
            if path_obj == parent:
                # allow this folder because a subfolder is an authorized folder
                ok = True
                if prev_parent:
                    # save the authorized folder name (previous parent)
                    rem_parts_0.append(prev_parent.name)
                break
            prev_parent = parent

    if not ok:
        raise Http404

    global google_drive_files
    google_drive_files = cache.get("google_drive_files") or google_drive_files

    ok_parts = []
    file_tree: dict | tuple[dict, dict] | None = google_drive_files
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
            # fetch the files
            populate_file_list(request, file_id, ok_parts)
        except KeyError:
            raise Http404

    cache.set("google_drive_files", google_drive_files)

    if not ok_all:
        file_tree = (
            {k: v for k, v in file_tree[0].items() if k in rem_parts_0},
            {k: v for k, v in file_tree[1].items() if v["name"] in rem_parts_0},
        ) if isinstance(file_tree, tuple) else (
            file_tree if file_tree["name"] in rem_parts_0 else None
        )

    if file_tree is None:
        raise Http404

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
