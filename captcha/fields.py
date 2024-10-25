import logging
import sys
from urllib.error import HTTPError

from captcha.client import submit
from captcha.constants import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY
from captcha.widgets import HCaptchaWidget
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class HCaptchaField(forms.CharField):
    """
    Field that displays a hCaptcha and checks it.
    """

    widget = HCaptchaWidget
    default_error_messages = {
        "captcha_invalid": _("Error verifying hCaptcha, please try again."),
        "captcha_error": _("Error verifying hCaptcha, please try again."),
    }

    def __init__(self, *args, public_key=None, private_key=None, **kwargs):
        """
        HCaptchaField can accepts attributes which is a dictionary of attributes to be passed
        to the hCaptcha widget class.

        See https://docs.hcaptcha.com/configuration/#hcaptcha-container-configuration for more information.
        """
        super().__init__(*args, **kwargs)

        # hCaptcha fields are always required.
        self.required = True

        # Setup instance variables.
        self.private_key = private_key or getattr(settings, "HCAPTCHA_PRIVATE_KEY", TEST_PRIVATE_KEY)
        self.public_key = public_key or getattr(settings, "HCAPTCHA_PUBLIC_KEY", TEST_PUBLIC_KEY)

        # Update widget attrs with data-sitekey.
        self.widget.attrs["data-sitekey"] = self.public_key

    def get_remote_ip(self):
        """
        Return the remote IP address for passing to hCaptcha API.
        """
        f = sys._getframe()
        while f:
            request = f.f_locals.get("request")
            if request:
                remote_ip = request.META.get("REMOTE_ADDR", "")
                forwarded_ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
                return remote_ip if not forwarded_ip else forwarded_ip
            f = f.f_back
        return ""

    def validate(self, value: str):
        if settings.OFFLINE:
            return

        super().validate(value)

        try:
            check_captcha = submit(
                hcaptcha_response=value,
                private_key=self.private_key,
                remoteip=self.get_remote_ip(),
            )
        except HTTPError as exc:  # Catch timeouts, etc
            raise ValidationError(self.error_messages["captcha_error"], code="captcha_error") from exc

        if not check_captcha.is_valid:
            logger.warning("hCaptcha validation failed due to: %s", check_captcha.error_codes)
            raise ValidationError(self.error_messages["captcha_invalid"], code="captcha_invalid")

        required_score = self.widget.attrs.get("required_score")
        if required_score:
            # Our score values need to be floats, as that is the expected
            # response from the hCaptcha endpoint. Rather than ensure that on
            # the widget, we do it on the field to better support user
            # subclassing of the widgets.
            required_score = float(required_score)

            # If a score was expected but non was returned, default to a 1,
            # which is the highest score that it can return. This is to do our
            # best to assure a failure here, we can not assume that a form
            # that needed the threshold should be valid if we didn't get a
            # value back.
            score = float(check_captcha.data.get("score", 1))

            if score >= required_score:
                logger.warning(
                    "hCaptcha validation failed due to its score of %s being greater than the required amount.",
                    score,
                )
                raise ValidationError(self.error_messages["captcha_invalid"], code="captcha_invalid")
