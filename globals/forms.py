from captcha.fields import HCaptchaField
from django import forms


class ContactCaptchaForm(forms.Form):
    captcha = HCaptchaField()
