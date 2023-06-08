from django import forms
from django.contrib import admin

from website.widgets import MarkdownEditor

from .models import Page


class PageAdminForm(forms.ModelForm):
    """
    Form in the admin interface for pages (with Markdown editor).
    """

    model = Page

    class Meta:
        widgets = {
            "content": MarkdownEditor(),
        }


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """
    Admin interface for pages.
    """

    form = PageAdminForm
