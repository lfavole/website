from django import forms
from captcha.fields import ReCaptchaField


class ContactCaptchaForm(forms.Form):
    captcha = ReCaptchaField()
