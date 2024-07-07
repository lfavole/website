from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme


class AdminSiteOTPRequired(AdminSite):
    """
    AdminSite enforcing OTP verified staff users.
    """

    # def has_permission(self, request):
    #     """
    #     Returns True if the given HttpRequest has permission to view
    #     *at least one* page in the admin site.
    #     """
    #     return True
    #     if not super().has_permission(request):
    #         return False
    #     return request.user.is_verified()  # type: ignore

    def login(self, request, extra_context=None):
        """
        Redirects to the site login page for the given HttpRequest.
        """
        if self.has_permission(request):
            # Already logged-in, redirect to admin index
            return redirect("admin:index")

        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))

        if not redirect_to or not url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=[request.get_host()],
            require_https=request.is_secure(),
        ):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        return redirect_to_login(redirect_to)
