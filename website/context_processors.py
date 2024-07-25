from django.conf import settings
from django.utils.timezone import now
from website.utils.connectivity import internet


def globals(request):
    """Adds global variables to all templates."""
    from django.contrib import admin

    return {
        "offline": False if settings.OFFLINE else not internet(),
        "now": now(),
        # True if the user can view at least one page in the admin site
        "admin_permission": admin.site.has_permission(request),
        "CSP_NONCE": getattr(request, "_csp_nonce", ""),
        # "status" variables (production, debug...)
        **{var: getattr(settings, var) for var in ("GITHUB_REPO", "SENTRY_SDK", "PRODUCTION", "DEVELOPMENT", "DEBUG")},
    }
