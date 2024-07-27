from collections import defaultdict
from functools import lru_cache

from temperatures.models import Temperature


def get_all_temperatures_data(temperatures: list[Temperature]):
    """Return a list containing the data about all the given temperatures."""
    data = []

    for temp in temperatures:
        to_add = [
            temp.date.year,
            temp.date.month - 1,  # JavaScript month (begins with 0)
            temp.date.day,
            temp.temperature,
            temp.weather.lower(),
            temp.snow_cm,
            temp.max_temp,
        ]
        # clean up unuseful data
        while not to_add[-1]:
            to_add.pop()
        data.append(to_add)

    return data


def get_weather_counts(temperatures: list[Temperature]):
    """Return a list containing the weather counts for all the given temperatures."""

    # recreate this function here so the cache is reset between pages
    # and the language can change
    @lru_cache
    def _get_weather_verbose_name(weather: str):
        """Return the verbose name for a weather."""
        for field in Temperature._meta.fields:
            if field.name == "weather":
                for choice in field.choices:
                    if choice[0] == weather:
                        # evaluate the translation (which is a proxy)
                        # to avoid JSON serialization errors
                        return str(choice[1])

        raise ValueError(f"Weather {weather!r} not found")

    weather_counts = defaultdict(lambda: 0)

    for temp in temperatures:
        weather_counts[_get_weather_verbose_name(temp.weather)] += 1

    return weather_counts
