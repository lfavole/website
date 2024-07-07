import time

from django.http.response import HttpResponse, HttpResponseForbidden


def debug(request):
    """
    Display debug information.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    ret = f"{request=}\n\n"
    for prop in dir(request):
        ret += f"request.{prop}={getattr(request, prop)}\n"
    return HttpResponse(ret, "text/plain")


def wait(request, seconds=5):
    """
    Wait a specified number of seconds.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    time.sleep(seconds)
    return HttpResponse("success")
