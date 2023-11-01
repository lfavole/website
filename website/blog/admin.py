from typing import Type
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from tinymce.widgets import AdminTinyMCE

from .models import File, Image, Page


class DataInline(GenericTabularInline):
    """
    Inline for files/images.
    """

    model: Type[File] | Type[Image]
    readonly_fields = ("file",)
    extra = 0

    @property
    def ma(self):
        # ModelAdmin of the parent object
        return admin.site._registry[self.parent_model]

    def has_add_permission(self, request, obj: File | Image | None):
        if self.ma and (self.ma.has_add_permission(request) or self.ma.has_change_permission(request, obj)):
            # we can add or change the parent object => we can add files/images
            return True
        return super().has_add_permission(request, obj)  # type: ignore

    def has_change_permission(self, request, obj: File | Image):
        if self.ma and self.ma.has_change_permission(request, obj):
            # we can change the parent object => we can change files/images
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj: File | Image):
        if self.ma and self.ma.has_change_permission(request, obj):
            # we can change the parent object => we can delete files/images
            return True
        return super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj: File | Image):
        if self.ma and self.ma.has_view_permission(request, obj):
            # we can view the parent object => we can view files/images
            return True
        return super().has_view_permission(request, obj)


class FilesInline(DataInline):
    """
    Inline for files.
    """

    model = File


class ImagesInline(DataInline):
    """
    Inline for images.
    """

    model = Image


class PageAdminForm(forms.ModelForm):
    """
    Form in the admin interface for pages (with TinyMCE editor).
    """

    model = Page

    class Meta:
        widgets = {
            "content": AdminTinyMCE(),
        }


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """
    Admin interface for pages.
    """

    form = PageAdminForm
    inlines = [ImagesInline, FilesInline]
