from typing import Type

from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from tinymce.widgets import AdminTinyMCE

from .models import File, Image, Page


class DataMixin:
    model: Type[File] | Type[Image]
    fields = ("file",)

    def get_modeladmin(self, obj):
        if isinstance(self, InlineModelAdmin):
            # ModelAdmin of the parent object
            return admin.site._registry[self.parent_model]
        return admin.site._registry[type(obj.item)] if obj else None

    def has_add_permission(self, request, obj: File | Image | None = None):
        ma = self.get_modeladmin(obj)
        if ma and (ma.has_add_permission(request) or ma.has_change_permission(request, obj)):
            # we can add or change the parent object => we can add files/images
            return True
        try:
            return super().has_add_permission(request, obj)  # type: ignore
        except TypeError:
            return super().has_add_permission(request)  # type: ignore

    def has_change_permission(self, request, obj: File | Image | None = None):
        ma = self.get_modeladmin(obj)
        if ma and ma.has_change_permission(request, obj):
            # we can change the parent object => we can change files/images
            return True
        return super().has_change_permission(request, obj)  # type: ignore

    def has_delete_permission(self, request, obj: File | Image | None = None):
        ma = self.get_modeladmin(obj)
        if ma and ma.has_change_permission(request, obj):
            # we can change the parent object => we can delete files/images
            return True
        return super().has_delete_permission(request, obj)  # type: ignore

    def has_view_permission(self, request, obj: File | Image | None = None):
        ma = self.get_modeladmin(obj)
        if ma and ma.has_view_permission(request, obj):
            # we can view the parent object => we can view files/images
            return True
        return super().has_view_permission(request, obj)  # type: ignore


class DataInline(DataMixin, GenericTabularInline):
    """
    Inline for files/images.
    """

    readonly_fields = ("file",)
    extra = 0


@admin.register(File)
class FilesAdmin(DataMixin, admin.ModelAdmin):
    """
    Admin interface for files.
    """


@admin.register(Image)
class ImagesAdmin(DataMixin, admin.ModelAdmin):
    """
    Admin interface for images.
    """


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
