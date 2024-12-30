from django.contrib import admin

from .models import AuthorizedDelivering


@admin.register(AuthorizedDelivering)
class AuthorizedDeliveringAdmin(admin.ModelAdmin):
    readonly_fields = ("uuid",)
