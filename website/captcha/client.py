from typing import Any

import requests
from captcha.constants import DEFAULT_RECAPTCHA_DOMAIN
from django.conf import settings

RECAPTCHA_SUPPORTED_LANUAGES = ["en", "nl", "fr", "de", "pt", "ru", "es", "tr"]


class RecaptchaResponse:
    """
    A reCAPTCHA response.
    """

    def __init__(self, data: dict[str, Any]):
        self.data = data

    @property
    def is_valid(self):
        return self.data.pop("success")

    @property
    def error_codes(self):
        return self.data.pop("error-codes", None)


def submit(recaptcha_response: str, private_key: str, remoteip: str):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_response -- The value of reCAPTCHA response from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """
    params = {
        "secret": private_key,
        "response": recaptcha_response,
        "remoteip": remoteip,
    }
    domain = getattr(settings, "RECAPTCHA_DOMAIN", DEFAULT_RECAPTCHA_DOMAIN)
    response = requests.post(
        f"https://{domain}/recaptcha/api/siteverify",
        params=params,
        headers={"User-agent": "reCAPTCHA Django"},
        timeout=getattr(settings, "RECAPTCHA_VERIFY_REQUEST_TIMEOUT", 10),
        proxies=getattr(settings, "RECAPTCHA_PROXY", {}),
    )
    data = response.json()
    response.close()
    return RecaptchaResponse(data)
