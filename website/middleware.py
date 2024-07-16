import base64
import os
import random
from typing import Callable
from django.conf import settings
from django.utils.functional import SimpleLazyObject

from .csp import compile_csp

try:
    import minify_html
except ImportError:
    minify_html = None
from django.http import HttpRequest, HttpResponse


class MinifyHtmlMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if minify_html is not None and self.should_minify(request, response):
            content = response.content.decode(response.charset)
            response.content = minify_html.minify(
                content,
                minify_css=True,
                minify_js=True,
                do_not_minify_doctype=True,
            )
            if "Content-Length" in response:
                response["Content-Length"] = len(response.content)
        return response

    def should_minify(self, request: HttpRequest, response: HttpResponse) -> bool:
        return (
            not getattr(response, "streaming", False)
            and (request.resolver_match is None or getattr(request.resolver_match.func, "should_minify_html", True))
            and response.get("Content-Encoding", "") == ""
            and response.get("Content-Type", "").split(";", 1)[0] == "text/html"
        )


class CSPMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.csp = getattr(settings, "CONTENT_SECURITY_POLICY", None) or {}
        self.nonce = None

    def _get_nonce(self, request):
        """Return the nonce for the current request."""
        # ensure that subsequent calls return the same value
        nonce = getattr(request, "_csp_nonce", None)
        if nonce:
            return nonce

        nonce = base64.b64encode(os.urandom(16)).decode("ascii")
        request._csp_nonce = nonce
        return nonce

    def _check_overridable(self):
        """Raise if the CSP setting is a string and can't be overridden."""
        if isinstance(self.csp, str):
            raise ValueError("The CONTENT_SECURITY_POLICY setting is a string and can't be overridden")

    def override(self, csp_dict, request, response):
        """Override a CSP `dict`/`str` from a view by the CSP setting."""
        if isinstance(csp_dict, dict):
            csp_dict = {**csp_dict}  # make a copy
            if ... in csp_dict:
                self._check_overridable()
                csp_dict = {
                    **self.csp,
                    **csp_dict,
                }
                del csp_dict[...]
            for key, value in csp_dict.items():
                if callable(value):
                    csp_dict[key] = value(request, response)
                else:
                    csp_dict[key] = self.override(value, request, response)

        elif isinstance(csp_dict, (list, set, tuple)):
            csp_dict = [*csp_dict]  # make a copy and coerce everything to list
            if ... in csp_dict:
                if csp_dict.count(...) > 1:
                    raise ValueError("Too much ... in CSP override dict")
                self._check_overridable()
                i = csp_dict.index(...)
                csp_dict = [*csp_dict[:i], *self.csp, *csp_dict[i + 1 :]]
            for i, item in csp_dict:
                if callable(item):
                    csp_dict[i] = item(request, response)
                else:
                    csp_dict[i] = self.override(item, request, response)

        # skip overridding for strings, None, ...
        return csp_dict

    def add_csp_header(self, request, response):
        """Add the `Content-Security-Policy` or `Content-Security-Policy-Report-Only` header."""
        csp: dict | str = getattr(response, "csp", "") or ""

        # try to override the default CSP by the view parameters
        csp = self.override(csp, request, response) or {**self.csp}  # type: ignore

        if csp and not isinstance(csp, str):
            threshold = csp.get("report-threshold", 1)
            if not 0 <= threshold <= 1:
                raise ValueError(f"Wrong CSP threshold: {threshold}")
            # skip CSP reports if the threshold is zero
            if threshold == 0:
                return
            if threshold < 1 and "report-uri" in csp and random.random() >= threshold:
                del csp["report-uri"]

        # add the nonce
        if not isinstance(csp, str) and self.nonce is not None:
            pass  # TODO

        # set the `Content-Security-Policy-Report-Only` header if `report-only` is true
        header = (
            "Content-Security-Policy-Report-Only"
            if csp and not isinstance(csp, str) and csp.get("report-only")
            else "Content-Security-Policy"
        )
        # skip if the header has already been set
        if header in response:
            return

        # compile the CSP...
        policy = compile_csp(csp)

        # ...and set it
        if policy:
            response[header] = policy

    def process_response(self, request, response):
        """Process the response and add the CSP header."""
        self.add_csp_header(request, response)
        return response

    def __call__(self, request):
        self.nonce = SimpleLazyObject(lambda: self._get_nonce(request))
        return self.process_response(request, self.get_response(request))  # type: ignore
