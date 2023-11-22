from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TemperaturesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'temperatures'
    verbose_name = _("Temperature records")
