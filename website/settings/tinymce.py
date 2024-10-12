import re

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import LazyObject, lazy
from django.utils.translation import gettext

from .env import OFFLINE
from .files import STATIC_URL

# TinyMCE editor


class StylesheetsList(LazyObject, list):
    def _setup(self):
        from django.conf import settings
        from django.test.client import Client

        settings.ALLOWED_HOSTS.append("testserver")
        settings.SECURE_SSL_REDIRECT = False
        content = Client().get("/").content.decode()
        settings.ALLOWED_HOSTS.pop()
        settings.SECURE_SSL_REDIRECT = True

        self._wrapped = []
        for match in re.finditer(r'<link\b[^>]*\bhref=(["\']?)([^>]*)\1[^>]*>', content):
            if not re.search(r'rel=(["\']?)stylesheet\1', match.group(0)):
                continue
            self._wrapped.append(match.group(2))


static_lazy = lazy(static)
TINYMCE_JS_URL = (
    static_lazy("vendor/tinymce/tinymce.min.js")
    if OFFLINE  # type: ignore
    else "https://cdn.jsdelivr.net/npm/tinymce@7/tinymce.min.js"
)
TINYMCE_DEFAULT_CONFIG = {
    "base_url": STATIC_URL + "vendor/tinymce" if OFFLINE else "https://cdn.tiny.cloud/1/no-api-key/tinymce/7",
    "body_class": "content",
    "content_css": StylesheetsList(),
    "promotion": False,
    "plugins": "autolink code fullscreen help image link lists media preview quickbars save searchreplace table",
    "toolbar": (
        "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
        "aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor removeformat | "
        "image media link"
    ),
    "relative_urls": False,
    "valid_elements": "*[*]",
    "protect": [
        r"/<style>[\s\S]*?<\/style>/g",
        r"/<script>[\s\S]*?<\/script>/g",
    ],
    "image_advtab": True,
    "upload_image_url": reverse_lazy("tinymce-upload-image"),
    "license_key": "gpl",
}
