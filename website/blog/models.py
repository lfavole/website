from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Page(models.Model):
    """
    A blog page.
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
        slug_candidate = slug_original = slugify(value, allow_unicode=False)
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

    def __str__(self):
        return self.title
