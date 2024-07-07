from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GlobalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "globals"
    verbose_name = _("Global configuration")
