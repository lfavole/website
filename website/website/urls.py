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
from django.urls import include, path, re_path
from django.views.static import serve

from .views import (
    NewLogoutView,
    account_index,
    google,
    handler_404,
    handler_500,
    make_error,
    reload_website,
    robots,
    songs_list,
)

handler404 = handler_404
handler500 = handler_500

app_name = "website"
urlpatterns = i18n_patterns(
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/logout/", NewLogoutView.as_view()),
    path("admin/", admin.site.urls),
    # path("accounts/two-factor/", include("allauth_2fa.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/", account_index, name="account_index"),
    path("blog/", include("blog.urls", namespace="blog")),
    path("debug/", include("debug.urls", namespace="debug")),
    path("errors/", include("errors.urls", namespace="errors")),
    path("pseudos/", include("pseudos.urls", namespace="pseudos")),
    re_path("songs-list/(?P<path>.*)", songs_list),
    path("telegram-bot/", include("telegram_bot.urls", namespace="telegram_bot")),
    path("", include("home.urls", namespace="home")),
) + [
    path("google<str:id>.html", google),
    path("robots.txt", robots),
    path("500", make_error),
    path("reload-website", reload_website),
]

if not settings.DEBUG and not settings.PYTHONANYWHERE:
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
