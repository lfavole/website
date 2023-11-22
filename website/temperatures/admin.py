from django.contrib import admin

from .models import Temperature


@admin.register(Temperature)
class TemperatureAdmin(admin.ModelAdmin):
    list_display = ["date", "temperature", "weather", "wind", "hail"]
    list_filter = ["weather", "wind", "hail"]
    fields = [
        "date",
        "temperature",
        "weather",
        ("wind", "hail", "mist"),
        ("snow_cm", "max_temp"),
        "notes",
    ]
