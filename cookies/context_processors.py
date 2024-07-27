from django.http import HttpRequest

from .forms import CookiesForm


def cookies(request: HttpRequest):
    """Add cookies context variable to the context."""
    cookies = request.session.get("cookie_consent")
    return {
        "cookies_notset": cookies is None,
        "cookies": cookies or {},
        "cookies_form": CookiesForm() if cookies is None else getattr(request, "_cookies_form", None),  # type: ignore
    }
