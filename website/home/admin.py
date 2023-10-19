from functools import partial
from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db import models
from django.db.models.fields import Field
from tinymce.widgets import AdminTinyMCE

from .models import Link, SpecialContent


@admin.register(Link)
class LinkAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Admin interface for links.
    """


@admin.register(SpecialContent)
class SpecialContentAdmin(admin.ModelAdmin):
    """
    Admin interface for special contents.
    """

    def get_form(self, request, obj: SpecialContent | None = None, change=False, **kwargs):
        kwargs["formfield_callback"] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super().get_form(request, obj, change, **kwargs)

    def formfield_for_dbfield(self, db_field: Field, request=None, obj: SpecialContent | None = None, **kwargs):
        if obj and obj.slug == "home" and isinstance(db_field, models.TextField):
            kwargs["widget"] = AdminTinyMCE
        return super().formfield_for_dbfield(db_field, request, **kwargs)
