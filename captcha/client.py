from typing import Any

import requests
from django.conf import settings


class HCaptchaResponse:
    """
    A hCaptcha response.
    """

    def __init__(self, data: dict[str, Any]):
        self.data = data

    @property
    def is_valid(self):
        return self.data.pop("success")

    @property
    def error_codes(self):
        return self.data.pop("error-codes", None)


def submit(hcaptcha_response: str, private_key: str, remoteip: str):
    """
    Submits a hCaptcha request for verification. Returns HCcaptchaResponse
    for the request

    hcaptcha_response -- The value of hCaptcha response from the form
    private_key -- your hCaptcha private key
    remoteip -- the user's IP address
    """
    params = {
        "secret": private_key,
        "response": hcaptcha_response,
        "remoteip": remoteip,
    }
    response = requests.post(
        "https://api.hcaptcha.com/siteverify",
        params=params,
        headers={"User-agent": "hCaptcha Django"},
        timeout=getattr(settings, "HCAPTCHA_VERIFY_REQUEST_TIMEOUT", 10),
        proxies=getattr(settings, "HCAPTCHA_PROXY", {}),
    )
    data = response.json()
    response.close()
    return HCaptchaResponse(data)
