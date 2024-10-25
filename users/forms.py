from captcha.fields import HCaptchaField
from django import forms


class AllAuthSignupForm(forms.Form):
    captcha = HCaptchaField()

    def signup(self, *args, **kwargs):
        pass
