from django.core.exceptions import ValidationError
from django.db import models
from django.utils.formats import date_format, number_format
from django.utils.translation import gettext_lazy as _

from .fields import TemperatureField


class Temperature(models.Model):
    date = models.DateField(_("Date"))
    temperature = TemperatureField(_("Minimum temperature"))
    weather = models.CharField(_("Weather"), max_length=15, choices=[
        ("SUNNY", _("Sunny")),
        ("FEW_CLOUDS", _("Few clouds")),
        ("CLOUDY", _("Cloudy")),
        ("RAIN", _("Rain")),
        ("SNOW", _("Snow")),
    ], default="SUNNY")
    wind = models.BooleanField(_("Wind"))
    hail = models.BooleanField(_("Hail"))
    mist = models.BooleanField(_("Mist"))
    snow_cm = models.PositiveIntegerField(_("snow cm"), default=0)
    max_temp = TemperatureField(_("Maximum temperature"), blank=True, null=True)
    notes = models.TextField(_("Notes"), blank=True)

    def clean(self):
        if self.weather == "SNOW":
            if self.snow_cm == 0:
                raise ValidationError({
                    "snow_cm": _("You must specify the snow cm when it snows."),
                })
        else:
            self.snow_cm = 0

        if self.max_temp is not None:
            if self.temperature > self.max_temp:
                raise ValidationError({
                    "max_temp": _("The maximum temperature must be greater than the minimum temperature."),
                })

    def __str__(self):
        return f"{date_format(self.date)}{_(':')} {number_format(self.temperature)}°C"

    class Meta:
        verbose_name = _("temperature")
        ordering = ["date"]
