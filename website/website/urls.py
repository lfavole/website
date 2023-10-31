"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import re

from django.conf import settings
from django.contrib import admin
from django.urls import URLResolver, converters, include, path
from django.utils.translation import get_supported_language_variant
from django.utils.translation.trans_real import language_code_prefix_re
from django.views.static import serve

from .views import (
    NewLogoutView,
    account_index,
    export,
    google,
    handler_404,
    handler_500,
    make_error,
    redirect_lang_url,
    reload_website,
    robots,
    songs_list,
    upload_image,
)

handler404 = handler_404
handler500 = handler_500


class OptionalPathConverter:
    """
    Optional path that removes .php extension.
    """

    regex = r".*"

    def to_url(self, value: str):
        return value

    def to_python(self, value):
        return self.to_url(value)


converters.register_converter(OptionalPathConverter, "optpath")


class LocalePrefixPattern:
    converters = {}
    name = None

    @property
    def regex(self):
        # This is only used by reverse() and cached in _reverse_dict.
        return re.compile("^" + language_code_prefix_re.pattern[2:])

    def match(self, path):
        match = re.match("^" + language_code_prefix_re.pattern[2:], path)
        if not match:
            return None

        lang_code = match.group(1)
        try:
            get_supported_language_variant(lang_code)
            path = path[len(lang_code) + 1 :]
            return path, (), {"path": path}
        except LookupError:
            return None

    def check(self):
        return []

    def describe(self):
        return "'{}'".format(self)

    def __str__(self):
        return "<language>/"


app_name = "website"
urlpatterns = [
    URLResolver(LocalePrefixPattern(), [path("<optpath:path>", redirect_lang_url)]),  # type: ignore
    path("500", make_error),
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/logout/", NewLogoutView.as_view()),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", account_index, name="account_index"),
    path("blog/", include("blog.urls", namespace="blog")),
    path("comments/", include("django_comments.urls")),
    path("debug/", include("debug.urls", namespace="debug")),
    path("debug/", include("debug_toolbar.urls")),
    path("errors/", include("errors.urls", namespace="errors")),
    path("export/<format>/<app_label>/<model_name>/<elements_pk>", export, name="export"),
    path("pseudos/", include("pseudos.urls", namespace="pseudos")),
    path("reload-website", reload_website),
    path("songs-list/<optpath:path>", songs_list),
    path("telegram-bot/", include("telegram_bot.urls", namespace="telegram_bot")),
    path("tinymce/upload-image", upload_image, name="tinymce-upload-image"),
    path("tinymce/", include("tinymce.urls")),
    path("google<str:id>.html", google),
    path("robots.txt", robots),
    path("", include("django.conf.urls.i18n")),
    path("", include("globals.urls")),
]

if not settings.PYTHONANYWHERE:
    if not settings.DEBUG:
        urlpatterns.append(
            path(
                settings.STATIC_URL.strip("/") + "/<path:path>",
                serve,
                {"document_root": settings.STATIC_ROOT},
            )
        )
    urlpatterns.append(
        path(
            settings.MEDIA_URL.strip("/") + "/<path:path>",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        )
    )
