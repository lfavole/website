from adminsortable2.admin import SortableAdminMixin
from django import forms
from django.contrib import admin

from website.widgets import MarkdownEditor

from .models import Link, SpecialContent


@admin.register(Link)
class LinkAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Admin interface for links.
    """


class SpecialContentAdminForm(forms.ModelForm):
    """
    Form in the admin interface for special contents (with Markdown editor).
    """

    model = SpecialContent

    class Meta:
        widgets = {
            "content": MarkdownEditor(),
        }


@admin.register(SpecialContent)
class SpecialContentAdmin(admin.ModelAdmin):
    """
    Admin interface for special contents.
    """

    form = SpecialContentAdminForm
