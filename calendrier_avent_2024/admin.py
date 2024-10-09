from django.contrib import admin

from .models import Day


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    pass
