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

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import URLPattern, converters, include, path
from django.views.static import serve

from .views import (
    account_index,
    export,
    google,
    handler_404,
    handler_500,
    make_error,
    reload_website,
    robots,
    songs_list,
    upload_image,
)

handler404 = handler_404
handler500 = handler_500


class OptionalPathConverter:
    """
    Optional path (path that can be empty).
    """

    regex = r".*"

    def to_url(self, value: str):
        return value

    def to_python(self, value):
        return self.to_url(value)


converters.register_converter(OptionalPathConverter, "optpath")


app_name = "website"
urlpatterns: list[list[URLPattern] | URLPattern] = i18n_patterns(
    path("500", make_error),
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", account_index, name="account_index"),
    path("blog/", include("blog.urls", namespace="blog")),
    path("calendrier-avent-2023/", include("calendrier_avent_2023.urls", namespace="calendrier_avent_2023")),
    path("comments/", include("django_comments.urls")),
    path("debug/", include("debug.urls", namespace="debug")),
    path("debug/", include("debug_toolbar.urls")),
    path("export/<format>/<app_label>/<model_name>/<elements_pk>", export, name="export"),
    path("pseudos/", include("pseudos.urls", namespace="pseudos")),
    path("reload-website", reload_website),
    path("songs-list/<optpath:path>", songs_list),
    path("telegram-bot/", include("telegram_bot.urls", namespace="telegram_bot")),
    path("temperatures/", include("temperatures.urls", namespace="temperatures")),
    path("tinymce/upload-image", upload_image, name="tinymce-upload-image"),
    path("tinymce/", include("tinymce.urls")),
    path("google<str:id>.html", google),
    path("robots.txt", robots),
    path("", include("django.conf.urls.i18n")),
    path("", include("globals.urls")),
    prefix_default_language=False,
)  # type: ignore

if not settings.PRODUCTION:
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
