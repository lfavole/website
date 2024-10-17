from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

from django.http.response import HttpResponseBase

ViewFunc = TypeVar("ViewFunc", bound=Callable[..., HttpResponseBase])


def no_html_minification(view_func: ViewFunc) -> ViewFunc:
    """
    Mark a view function as excluded from minification by MinifyHtmlMiddleware.
    """

    def wrapped_view(*args: Any, **kwargs: Any) -> HttpResponseBase:
        return view_func(*args, **kwargs)

    wrapped_view.should_minify_html = False  # type: ignore[attr-defined]
    return cast(
        ViewFunc,
        wraps(view_func)(wrapped_view),
    )


def csp(directives: dict | str | None):
    def decorator(view_func: ViewFunc) -> ViewFunc:
        """Add custom CSP directives to a view."""

        def wrapped_view(*args: Any, **kwargs: Any) -> HttpResponseBase:
            ret = view_func(*args, **kwargs)
            ret.csp = directives  # type: ignore
            return ret

        return cast(
            ViewFunc,
            wraps(view_func)(wrapped_view),
        )
    return decorator

# Exclude WebAuthn views from CSP
from allauth.mfa.webauthn import views
views.AddWebAuthnView.get = csp(None)(views.AddWebAuthnView.get)
views.AddWebAuthnView.post = csp(None)(views.AddWebAuthnView.post)
views.signup_webauthn = csp(None)(views.signup_webauthn)
