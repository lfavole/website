from captcha.fields import ReCaptchaField
from django import forms


class AllAuthSignupForm(forms.Form):
    captcha = ReCaptchaField()

    def signup(self, *args, **kwargs):
        pass
