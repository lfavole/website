import base64
import logging
import os
import random
from typing import Callable, TypeVar
from django.conf import settings

from .csp import CSP_SOURCES, InvalidCSPError, compile_csp

try:
    import minify_html
except ImportError:
    minify_html = None
from django.http import HttpRequest, HttpResponse

logger = logging.Logger(__name__)


class MinifyHtmlMiddleware:
    sync_capable = True
    async_capable = True
    prefixes = {
        "text/html": "",
        "text/css": "<style>",
        "text/javascript": "<script>",
    }

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if minify_html is not None and self.should_minify(request, response):
            content = response.content.decode(response.charset)
            prefix = self.prefixes[self.get_content_type(response)]
            try:
                response.content = minify_html.minify(
                    prefix + content,
                    minify_css=True,
                    minify_js=True,
                    do_not_minify_doctype=True,
                ).removeprefix(prefix)
            except:
                # if there is an error during the minification, skip it silently
                pass
            else:
                if "Content-Length" in response:
                    response["Content-Length"] = len(response.content)
        return response

    def get_content_type(self, response):
        return response.get("Content-Type", "").split(";", 1)[0]

    def should_minify(self, request: HttpRequest, response: HttpResponse) -> bool:
        return (
            not getattr(response, "streaming", False)
            and (request.resolver_match is None or getattr(request.resolver_match.func, "should_minify_html", True))
            and response.get("Content-Encoding", "") == ""
            and self.get_content_type(response) in self.prefixes
        )


K = TypeVar("K")
V = TypeVar("V")


class CSPNoncesDict(dict[K, V]):
    """
    A `dict` that contains CSP nonces for different sources.

    This class behaves like `defaultdict` but takes the key as an argument
    so errors can be raised when the nonce is fetched.
    """
    def __init__(self, generator: Callable[[K], V]):
        self.generator = generator

    def __getitem__(self, key):
        if key not in self:
            self[key] = self.generator(key)
        return super().__getitem__(key)

    def __repr__(self):
        return f"CSPNoncesDict({super().__repr__()})"


class CSPMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.csp = getattr(settings, "CONTENT_SECURITY_POLICY", None) or {}

    def _generate_nonce(self, source):
        """Return a randomly generated nonce for a given source."""
        if source not in CSP_SOURCES:
            raise InvalidCSPError(f"The source '{source}' is not a valid CSP source")
        # we use a multiple of 3 so there are no "=" at the end of the nonce
        return base64.b64encode(os.urandom(15)).decode("ascii")

    def _get_nonces_dict(self, request):
        """Return the nonce for the current request."""
        # ensure that subsequent calls return the same value
        nonces_dict = getattr(request, "_csp_nonces", None)
        if nonces_dict:
            return nonces_dict

        nonces_dict = CSPNoncesDict(self._generate_nonce)
        request._csp_nonces = nonces_dict
        return nonces_dict

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

    def should_remove_report_uri(self, csp: dict | str):
        """Return `True` if we should remove the `report-uri` CSP parameter, `False` otherwise."""
        if not csp:
            return False
        if isinstance(csp, str):
            return False
        threshold = csp.get("report-threshold", 1)
        if not 0 <= threshold <= 1:
            raise ValueError(f"Wrong CSP threshold: {threshold}")
        # skip CSP reports if the threshold is zero
        if threshold == 0:
            return False
        if threshold < 1 and "report-uri" in csp and random.random() >= threshold:
            return True

    def add_csp_header(self, request, response):
        """Add the `Content-Security-Policy` or `Content-Security-Policy-Report-Only` header."""
        csp: dict | str = getattr(response, "csp", "") or ""

        # try to override the default CSP by the view parameters
        csp = self.override(csp, request, response) or {**self.csp}  # type: ignore

        if self.should_remove_report_uri(csp):
            assert isinstance(csp, dict)
            del csp["report-uri"]

        # add the nonce
        warned = False
        for source, nonce in self._get_nonces_dict(request).items():
            if isinstance(csp, str):
                # warn only once
                if not warned:
                    logger.warn("Trying to add the nonce but the CSP is a string. Skipping.")
                    warned = True
            else:
                csp.setdefault(f"{source}-src", []).append(f"nonce-{nonce}")

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
        # create the nonces dict
        self._get_nonces_dict(request)
        return self.process_response(request, self.get_response(request))  # type: ignore
