from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from tinymce.widgets import AdminTinyMCE

from .models import File, Image, Page


class DataInline(GenericTabularInline):
    """
    Inline for files/images.
    """
    readonly_fields = ("file",)
    extra = 0

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False


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
