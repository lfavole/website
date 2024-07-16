import os
from django.conf import settings

from django.utils.timezone import now

from globals.models import Page
from website.utils.connectivity import internet

NavLinks = list[tuple[Page, "NavLinks"]]


def offline(_request):
    """
    Add an `offline` variable to all templates.
    """
    return {"offline": not internet()}


def now_variable(_request):
    """
    Add a `now` variable to all templates.
    """
    return {"now": now()}


def nav_links(_request) -> dict[str, NavLinks]:
    """
    Add a `nav_links` variable to all templates.

    This variable must be used with the `nav` filter.
    """
    links_list = list(Page.objects.all())

    def get_links(parent):
        links_query = [link for link in links_list if link.parent_page == parent]
        links = []
        for link in links_query:
            if link != parent:  # avoid recursive links
                links.append((link, get_links(link)))
        return links

    return {"nav_links": get_links(None)}


def admin_permission(request):
    """
    Add an `admin_permission` variable to all templates.

    This variable is `True` if the user can view at least one page in the admin site.
    """
    from django.contrib import admin

    return {"admin_permission": admin.site.has_permission(request)}


def github_repo_url(request):
    """
    Add a `github_repo` variable to all templates.
    """
    return {"github_repo": os.environ.get("GITHUB_REPO")}


def sentry_sdk(request):
    """
    Add a `SENTRY_SDK` variable to all templates.
    """
    return {"SENTRY_SDK": settings.SENTRY_SDK}

def csp_nonce(request):
    """
    Add a `CSP_NONCE` variable to all templates.
    """
    return {"CSP_NONCE": getattr(request, "_csp_nonce", "")}
