from urllib.parse import urlencode

from django.forms import widgets


class HCaptchaWidget(widgets.Widget):
    """
    hCaptcha widget.

    public_key -- String value: can optionally be `"PASSED"` to not make use of the project wide hCaptcha sitekey.
    """

    template_name = "captcha/widget.html"

    def __init__(self, *args, api_params=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_params = api_params or {}

    def value_from_datadict(self, data, files, name):
        return data.get("h-captcha-response", None)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update(
            {
                "public_key": self.attrs["data-sitekey"],
                "api_params": urlencode(self.api_params),
            }
        )
        return context
