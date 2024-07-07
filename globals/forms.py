from captcha.fields import ReCaptchaField
from django import forms


class ContactCaptchaForm(forms.Form):
    captcha = ReCaptchaField()
