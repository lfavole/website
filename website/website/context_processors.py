import custom_settings
from django.utils.timezone import now
from globals.models import Page

NavLinks = list[tuple[Page, "NavLinks"]]


def offline(_request):
    """
    Add an `offline` variable to all templates.
    """
    return {"offline": custom_settings.OFFLINE}


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
    Add an `github_repo` variable to all templates.
    """
    return {"github_repo": custom_settings.GITHUB_REPO}
