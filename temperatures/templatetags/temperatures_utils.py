import datetime as dt
import re

from django import template
from django.utils.html import escapejs
from django.utils.safestring import mark_safe
from temperatures.models import Temperature

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


def get_js_timestamp(value: dt.date):
    """
    Return a JavaScript timestamp for the given date in UTC timezone.
    """
    return int(dt.datetime.combine(value, dt.time()).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def _none_empty(value):
    """
    Return "" for None or the original value.
    """
    return "" if value is None else value


def _replace_all(value: str, old: str, new: str):
    while len(value) != len(data := value.replace(old, new)):
        pass
    return value


@register.simple_tag
def get_all_temperatures():
    all_temperatures = list(Temperature.objects.all())

    if not all_temperatures:
        return ""

    data = ""
    first_day = all_temperatures[0]
    now = dt.date.today()
    date = first_day.date

    temps_displayed = 0

    weathers_count = {}

    while date <= now:
        temps_for_date = [temp for temp in all_temperatures if temp.date == date]

        if len(temps_for_date):
            temp = temps_for_date[0]
            weather = temp.weather
            if weather not in weathers_count:
                weathers_count[weather] = 0
            weathers_count[weather] += 1
            data += (
                "["
                + ",".join(
                    str(el)
                    for el in [
                        temp.date.year,
                        temp.date.month - 1,
                        temp.date.day,
                        temp.temperature,
                        f'"{temp.weather.lower()}"',
                        temp.snow_cm if temp.weather == "SNOW" else "",
                        _none_empty(temp.max_temp),
                    ]
                )
                + "],"
            )
            data = re.sub(r"\.0([,\]])", r"\1", data)
            data = re.sub(r",+\]", "]", data)
            data = re.sub(r"([\[,])0\.", r"\1.", data)
            # data = _replace_all(data, ",]", "]")
            # data = _replace_all(data, ".0,", ",")

        temps_displayed += len(temps_for_date)
        if temps_displayed == len(all_temperatures):
            break

        date += dt.timedelta(days=1)

    weathers_js = ""
    for weather, count in weathers_count.items():
        weather_choice_name = ""
        for field in Temperature._meta.fields:
            if field.name == "weather":
                for choice in field.choices:
                    if choice[0] == weather:
                        weather_choice_name = choice[1]
                        break
                break
        weathers_js += f'["{escapejs(weather_choice_name)}",{count}],'

    return mark_safe(f"var data=[{data[:-1]}],weather=[{weathers_js[:-1]}];")
