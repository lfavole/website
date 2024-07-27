import datetime as dt
import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from ..counts import get_all_temperatures_data, get_weather_counts
from ..models import Temperature

register = template.Library()


@register.simple_tag
def missing_extra_days():
    missing: list[dt.date] = []
    extra: list[dt.date] = []

    all_temperatures = list(Temperature.objects.all())

    if not all_temperatures:
        return mark_safe('<div id="days"></div>')

    first_day = all_temperatures[0]
    now = dt.date.today()
    date = first_day.date
    while date <= now:
        temperatures_for_date = [temp for temp in all_temperatures if temp.date == date]
        if len(temperatures_for_date) == 0:
            missing.append(date)
        elif len(temperatures_for_date) >= 2:
            extra.append(date)
        date += dt.timedelta(days=1)

    def pluriel(n: int):
        return str(n) + " jour" + ("s" if n >= 2 else "")

    ret = '<div id="days">'

    if missing:
        ret += f'<p class="missing">Il manque {pluriel(len(missing))} : '
        for jour in missing:
            ret += f'<a href="?date={jour}">{jour.day:02d}/{jour.month:02d}</a>, '
        ret = ret[:-2]
        ret += "</p>"

    if extra:
        ret += f'<p class="extra">Il y a {pluriel(len(extra))} en trop : '
        for jour in extra:
            ret += f'<a href="?date={jour}">{jour.day:02d}/{jour.month:02d}</a>, '
        ret = ret[:-2]
        ret += "</p>"

    ret += "</div>"

    return mark_safe(ret)


@register.simple_tag
def get_all_temperatures():
    temperatures = list(Temperature.objects.all())
    return mark_safe(
        json.dumps(
            {
                "data": get_all_temperatures_data(temperatures),
                "weather": list(get_weather_counts(temperatures).items()),
            },
            cls=DjangoJSONEncoder,
            separators=(",", ":"),
        )
    )
