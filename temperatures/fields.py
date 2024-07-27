from typing import Any

from django import forms
from django.db import models
from django.utils.safestring import mark_safe


class DateInput(forms.DateInput):
    input_type = "date"


class TemperatureField(models.FloatField):
    def formfield(self, *args, **kwargs):
        kwargs["widget"] = TemperatureInput
        return super().formfield(*args, **kwargs)


class TemperatureInput(forms.NumberInput):
    """A number input that has a step of 0.1 and has '°C' just after it."""

    def __init__(self, attrs: dict[str, Any] = {}):
        super().__init__(attrs={"step": 0.1, **attrs})

    def render(self, *args, **kwargs):
        # font-size is for Django administration
        return super().render(*args, **kwargs) + mark_safe(' <span style="font-size:1rem;margin-left:0.5em">°C</span>')
