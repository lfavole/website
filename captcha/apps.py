from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _

from .checks import hcaptcha_key_check


class CaptchaConfig(AppConfig):
    name = "captcha"
    verbose_name = _("Django hCaptcha")

    def ready(self):
        register(hcaptcha_key_check, Tags.security)
