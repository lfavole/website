from debug_toolbar.panels.history import views as history_views
from debug_toolbar.settings import PANELS_DEFAULTS
from debug_toolbar.toolbar import DebugToolbar
from django.http import HttpRequest
from django.template.loader import render_to_string

# Debug toolbar settings
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "website.settings.show_toolbar",
    "SHOW_COLLAPSED": True,
    "RENDER_PANELS": False,
}
DEBUG_TOOLBAR_PANELS = [
    *PANELS_DEFAULTS,
    "debug.panels.DebugModePanel",
    "debug.panels.ErrorPanel",
    "debug.panels.GitInfoPanel",
]


def new_render_to_string(*args, **kwargs):
    ret = render_to_string(*args, **kwargs)
    try:
        import minify_html
    except ImportError:
        return ret
    ret = minify_html.minify(
        ret,
        minify_css=True,
        minify_js=True,
        do_not_minify_doctype=True,
    )
    return ret


history_views.render_to_string = new_render_to_string


def show_toolbar(request: HttpRequest):
    """
    Should we show the toolbar?
    """
    return request.user.is_authenticated and request.user.has_perm("users.can_see_debug_toolbar")  # type: ignore


def observe_request(request: HttpRequest):
    """
    Should we observe the request with the toolbar?
    """
    if DebugToolbar.is_toolbar_request(request):
        return False
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return False
    return True
