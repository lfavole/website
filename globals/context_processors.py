from .models import Page

NavLinks = list[tuple[Page, "NavLinks"]]


def nav_links(_request) -> dict[str, NavLinks]:
    """
    Add a `nav_links` variable to all templates.

    This variable must be used with the `nav` filter.
    """
    links_list = list(Page.objects.select_related("parent_page"))

    def get_links(parent):
        links_query = [link for link in links_list if link.parent_page == parent]
        links = []
        for link in links_query:
            if link != parent:  # avoid recursive links
                links.append((link, get_links(link)))
        return links

    return {"nav_links": get_links(None)}
