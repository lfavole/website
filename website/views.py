import datetime as dt
import hmac
import importlib
import mimetypes
import os.path
import sys
import traceback
from hashlib import sha256
from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Type
from urllib.parse import quote, urljoin, urlparse
from wsgiref.util import is_hop_by_hop

import requests
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.serializers import get_serializer
from django.db.models import Model
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Engine, RequestContext
from django.urls import resolve
from django.utils.encoding import force_bytes
from django.utils.translation import get_language_from_path
from django.utils.translation import gettext_lazy as _
from django.views.debug import technical_404_response
from django.views.decorators.csrf import csrf_exempt
from sentry_sdk import Hub

from blog.models import Image
from website.utils.http import encode_filename
from website.utils.permission import has_permission

from .errors import TestError

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    fetch = importlib.import_module(".fetch", "scripts").main
except ImportError:
    fetch = None

DATA = Path(__file__).resolve().parent.parent.parent / "data"


def google(_request, id):
    """Return the Google site verification file."""
    if os.getenv("GOOGLE_SITE_VERIFICATION_ID", "") == id:
        return HttpResponse(f"google-site-verification: google{os.getenv('GOOGLE_SITE_VERIFICATION_ID')}.html")
    google_file = DATA / f"google{id}.html"
    if google_file.exists():
        return FileResponse(google_file.open("rb"))
    raise Http404()


def make_error(request):
    """
    This view doesn't return a page, it always fails with `TestError`.
    """
    if 1 + 1 == 2:
        Hub._current.last_event_id = None
        raise TestError("Test of the 500 error page")
    # this will never be called but will hide the type checker error in urls.py
    return HttpResponse()


def handler_404(request, exception):
    """
    404 (not found) error page.
    """
    if request.user and request.user.has_perm("can_see_traceback"):
        return technical_404_response(request, exception)
    return render(
        request,
        "website/404.html",
        {
            "request_path": quote(request.path),
            # "exception": exception_repr,
        },
        status=404,
    )


DEBUG_ENGINE = Engine(
    dirs=[str(Path(__file__).parent / "templates")],
    context_processors=["website.context_processors.globals"],
    debug=True,
    libraries={
        "i18n": "django.templatetags.i18n",
        "nav": "globals.templatetags.nav",
        "socialaccount": "allauth.socialaccount.templatetags.socialaccount",
        "static": "django.templatetags.static",
    },
)


def handler_500(request, _template_name=None):
    """
    500 (server error) page that logs the error.
    """
    try:
        with (Path(__file__).parent / "templates/website/500.html").open() as f:
            t = DEBUG_ENGINE.from_string(f.read())
        html = t.render(
            RequestContext(
                request,
                {
                    "error": True,
                    "error_id": Hub.current._last_event_id or "x" * 32,
                },
            )
        )
        return HttpResponse(html, status=500)
    except Exception:
        # print the exception to the logs
        traceback.print_exc()
        return HttpResponse(_("An unexpected error occured while trying to display the 500 error page."), "text/plain")


def account_index(request):
    return render(request, "account/index.html")


def export(request, format: str, app_label: str, model_name: str, elements_pk: str):
    # Run the operations that don't need the database first
    pk_list = None if elements_pk == "all" else elements_pk.split(",")
    serializer = get_serializer(format)()

    # import this now because it is assigned during serializers loading
    from django.core.serializers import _serializers

    for ext, module in _serializers.items():
        if module.__name__ == serializer.__module__:
            extension = ext
            break
    else:
        extension = "txt"
    if extension == "python":
        extension = "py"

    content_type = get_object_or_404(ContentType, app_label=app_label, model=model_name)
    model = content_type.model_class()

    if not model:
        raise Http404

    # Check for permission
    if not has_permission(request, model):
        if not settings.DEBUG:
            raise Http404
        return HttpResponseForbidden("Permission denied.")

    queryset = model.objects.all()
    if pk_list:
        queryset = queryset.filter(pk__in=pk_list)
    if model.__name__.lower() == "meeting":
        queryset2 = apps.get_model(model._meta.app_label, "Attendance").objects.filter(meeting__in=queryset)
        queryset = list(queryset) + list(queryset2)
    if not isinstance(queryset, list):
        queryset = list(queryset)

    response = HttpResponse()

    date = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"export_{content_type.app_label}_{content_type.model}_{date}.{extension}"
    response.headers["Content-Type"] = mimetypes.guess_type(f"x.{extension}")[0]  # type: ignore
    response.headers["Content-Disposition"] = "attachment; " + encode_filename(filename)  # type: ignore

    serializer.serialize(queryset, stream=response)
    return response


@csrf_exempt
def reload_website(request: HttpRequest):
    """
    Reload the website with a GET request (for superusers)
    or a POST requests (for GitHub webhook).
    """
    forbidden = HttpResponseForbidden("Permission denied.")
    key = settings.GITHUB_WEBHOOK_KEY
    if not fetch or not key:
        return forbidden

    # The superusers can reload the website
    if request.user.is_superuser:  # type: ignore
        return HttpResponse(fetch(pipe=True), "text/plain")

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    # Verify if request came from GitHub
    forwarded_for = request.headers.get("X-Forwarded-For")
    if not forwarded_for:
        return forbidden
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get("https://api.github.com/meta").json()["hooks"]

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return forbidden

    # Verify the request signature
    header_signature = request.headers.get("X-Hub-Signature-256")
    if header_signature is None:
        return forbidden

    sha_name, signature = header_signature.split("=", 1)
    if sha_name != "sha256":
        return HttpResponseServerError("Operation not supported.", status=501)

    mac = hmac.new(
        force_bytes(key),
        msg=force_bytes(request.body),
        digestmod=sha256,
    )
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return forbidden

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.headers.get("X-Github-Event", "ping")

    if event == "ping":
        return HttpResponse("pong", "text/plain")
    if event == "push":
        try:
            return HttpResponse(fetch(pipe=True), "text/plain")
        except:  # noqa
            return HttpResponseServerError("Failed to fetch changes")

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)


def robots(_request):
    """
    `robots.txt` file.
    """
    robots_file = Path(__file__).resolve().parent.parent / "robots.txt"
    if robots_file.exists():
        return FileResponse(robots_file.open("rb"))
    raise Http404()


import json
import requests
from django.http import JsonResponse
from urllib.parse import urlparse

SENTRY_HOST = ""
SENTRY_PROJECT_IDS = []

if settings.SENTRY_DSN:
    sentry_parsed = urlparse(settings.SENTRY_DSN)
    SENTRY_HOST = sentry_parsed.hostname
    SENTRY_PROJECT_IDS = [sentry_parsed.path.strip("/")]


def sentry(request):
    """Handle Sentry error reporting requests."""
    if not SENTRY_HOST:
        return JsonResponse({"error": "Sentry is not set up on the server"}, status=500)

    try:
        envelope = request.body.decode("utf-8")
        piece = envelope.split("\n")[0]
        header = json.loads(piece)
        dsn = urlparse(header["dsn"])
        project_id = dsn.path.strip("/")

        if dsn.hostname != SENTRY_HOST:
            raise ValueError(f"Invalid Sentry hostname: {dsn.hostname}")

        if not project_id or project_id not in SENTRY_PROJECT_IDS:
            raise ValueError(f"Invalid Sentry project ID: {project_id}")

        req = requests.post(f"https://{SENTRY_HOST}/api/{project_id}/envelope/", data=envelope)
        req.raise_for_status()

        return JsonResponse({}, status=200)

    except Exception:
        return JsonResponse({"error": "Error tunneling to Sentry"}, status=500)


def songs_list(request, path):
    """
    Proxy for GitHub repo containing songs.
    """
    base_path = "https://lfavole.github.io/songs-list/"
    req = requests.request(
        request.method,
        base_path + path,
        headers={"User-Agent": request.headers.get("User-Agent")},
        allow_redirects=False,
        stream=True,
    )
    resp = StreamingHttpResponse(
        req.iter_content(65536),
        content_type=req.headers["Content-Type"],
        status=req.status_code,
        reason=req.reason,
    )

    for k, v in req.headers.items():
        if k.lower() == "location":
            prefix = os.path.commonprefix([base_path, urljoin(base_path, v)])
            if prefix.removesuffix("/") == base_path.removesuffix("/"):
                resp[k] = v.removeprefix(prefix)
                continue
        if not is_hop_by_hop(k) and k.lower() != "content-encoding":
            resp[k] = v
    return resp


def upload_image(request: HttpRequest):
    """Handle TinyMCE image uploads."""
    # check the referrer URL: only the admin pages can send images
    referrer = urlparse(request.headers.get("Referer", ""))
    resolver_match = resolve(referrer.path)
    if resolver_match.app_name != "admin":
        raise PermissionDenied("The referrer URL is not an admin URL.")

    # try to get the model from the URL...
    try:
        model: Type[Model] | None = resolver_match.func.model_admin.model
    except AttributeError:
        model = None

    # ...and the primary key
    pk = resolver_match.kwargs.get("object_id")

    # only "change object" URLs can send images
    # (because they have a model and a primary key)
    if not model or pk is None or resolver_match.func.__name__ != "change_view":
        raise PermissionDenied("The referer URL is not a change URL.")

    # get the currently editing object...
    instance = model.objects.get(pk=pk)
    # ...and add the linked image
    image = Image.objects.create(item=instance, file=request.FILES["file"])

    # return the image URL
    return JsonResponse({"location": image.file.url})
