from django.db import models
from django.utils.translation import gettext_lazy as _

from website.utils.text import slugify


class BasePage(models.Model):
    """
    A page.
    """

    slug = models.SlugField(_("slug"), max_length=100, editable=False, unique=True)
    title = models.CharField(_("title"), max_length=100)
    content = models.TextField(_("content"), blank=True)
    hidden = models.BooleanField(_("hidden page"), default=False)

    def _generate_slug(self):
        """
        Generate a slug for a blog page (when creating).
        """
        value = self.title
        slug_candidate = slug_original = slugify(value)
        i = 0
        while True:
            i += 1
            if not type(self).objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = f"{slug_original}-{i}"

        return slug_candidate

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.slug = self._generate_slug()

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Page(BasePage):
    """
    A page / link (in the navbar).
    """

    order = models.PositiveIntegerField(_("order"), default=0, null=False)
    url = models.CharField(_("URL"), max_length=100, blank=True)
    parent_page = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("parent page"),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("page")
        ordering = ["order"]


class Setting(models.Model):
    """
    A special editable text (like the home page content).
    """

    slug = models.SlugField(_("slug"), max_length=100)
    title = models.CharField(_("title"), max_length=100)
    content = models.TextField(_("content"))

    def __str__(self):
        return _("Setting '%s'") % self.slug

    class Meta:
        verbose_name = _("special content")
        verbose_name_plural = _("special contents")
