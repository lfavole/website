from typing import Type
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def get_field(params):
    """Return a checkbox field for the given cookie category."""
    label, required = params
    if required:
        return forms.BooleanField(
            label=label, required=True, widget=forms.CheckboxInput({"checked": True, "disabled": True})
        )
    return forms.BooleanField(label=label, required=False)



CookiesForm: Type[forms.Form] = type(forms.Form)(
    "CookiesForm",
    (forms.Form,),
    {category: get_field(params) for category, params in settings.COOKIE_TYPES.items()},
)
