from functools import partial

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db import models
from django.db.models.fields import Field
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import AdminTinyMCE

from .models import Page, Setting


@admin.register(Page)
class PageAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Admin interface for pages.
    """

    formfield_overrides = {
        models.TextField: {"widget": AdminTinyMCE},
    }


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    """
    Admin interface for settings.
    """

    def get_form(self, request, obj: Setting | None = None, change=False, **kwargs):
        kwargs["formfield_callback"] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super().get_form(request, obj, change, **kwargs)

    def formfield_for_dbfield(self, db_field: Field, request=None, obj: Setting | None = None, **kwargs):
        if obj and (obj.slug in ("home", "contact") or obj.slug.startswith("25-12-")) and isinstance(db_field, models.TextField):
            kwargs["widget"] = AdminTinyMCE
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.action(description=_("Export selected %(verbose_name_plural)s"))
def export_selected(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    return redirect(
        "export",
        "json",
        meta.app_label,
        meta.model_name,
        ",".join(str(element.pk) for element in queryset),
    )


admin.site.add_action(export_selected)
