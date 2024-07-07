import datetime as dt

from django import forms
from temperatures.fields import DateInput, TemperatureInput

from .models import Temperature


def formfield_for_dbfield(db_field, **kwargs):
    if db_field.name == "date":
        # create a date field for today
        return forms.DateField(widget=DateInput, initial=str(dt.date.today()))
    return db_field.formfield(**kwargs)


class TemperaturesForm(forms.ModelForm):
    class Meta:
        model = Temperature
        exclude = []
        widgets = {
            "temperature": TemperatureInput({"autofocus": True}),
            "weather": forms.RadioSelect,
            "max_temp": TemperatureInput(),
        }
        formfield_callback = formfield_for_dbfield
        fieldsets = [
            ("date",),
            ("temperature",),
            ("weather",),
            ("wind", "hail", "mist"),
            ("snow_cm", "max_temp"),
            ("notes",),
        ]
