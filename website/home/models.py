from django.db import models
from django.utils.translation import gettext_lazy as _


class Link(models.Model):
    """
    A link (in the navbar).
    """

    order = models.PositiveIntegerField(_("order"), default=0, null=False)
    title = models.CharField(_("title"), max_length=100)
    url = models.CharField(_("URL"), max_length=100, blank=True)
    hidden = models.BooleanField(_("hidden link"), default=False)
    parent_link = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("parent link"),
    )

    class Meta:
        verbose_name = _("link")
        ordering = ["order"]

    def __str__(self):
        return self.title


class SpecialContent(models.Model):
    """
    A special editable text (like the home page content).
    """

    slug = models.SlugField(_("slug"), max_length=100)
    title = models.CharField(_("title"), max_length=100)
    content = models.TextField(_("content"))

    class Meta:
        verbose_name = _("special content")
        verbose_name_plural = _("special contents")
