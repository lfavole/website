from django import template
from django.shortcuts import resolve_url
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from website.context_processors import NavLinks

register = template.Library()


@register.filter
def nav(value: NavLinks):
    """
    Generate the HTML navbar from the return value of `nav_links`.
    """

    def nav_list(liste: NavLinks, indent=2):
        indent_str = "\t" * indent
        ret = f"{indent_str}<ul>\n"
        for page, nested_pages in liste:
            if page.url == "":
                if page.content == "":
                    href = "#"
                else:
                    href = resolve_url("page", page.slug)
            else:
                href = resolve_url(page.url)

            has_subpages_class = ' class="has-subpages"' if nested_pages else ""
            ret += f'{indent_str}\t<li{has_subpages_class}>\n{indent_str}\t\t<a href="{href}">'
            if page.hidden:
                ret += "<i>(<small>" + _("Hidden page:") + "</small> "
            ret += escape(page.title)
            if page.hidden:
                ret += ")</i>"
            ret += "</a>"

            if nested_pages:
                ret += "\n" + nav_list(nested_pages, indent + 2)
            ret += f"\n{indent_str}\t</li>\n"
        ret += f"{indent_str}</ul>\n"
        return ret

    # remove last newline
    return mark_safe(nav_list(value).rstrip())
