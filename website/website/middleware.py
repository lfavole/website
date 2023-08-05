from typing import Callable
from allauth_2fa.middleware import BaseRequire2FAMiddleware
from django.http import HttpRequest, HttpResponse
import minify_html


class RequireSuperuser2FAMiddleware(BaseRequire2FAMiddleware):
    def require_2fa(self, request):
        return True


class MinifyHtmlMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if self.should_minify(request, response):
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
