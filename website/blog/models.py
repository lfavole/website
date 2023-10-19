from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from storage.fields import ImageField


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

    def get_absolute_url(self):
        return reverse("blog:page", args=[self.pk])

    def __str__(self):
        return self.title


class Data(models.Model):
    """
    An file/image that is linked to an item.
    """

    file: models.FileField | ImageField
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    item = GenericForeignKey("content_type", "object_id")

    class Meta:
        abstract = True


class File(Data):
    """
    A file that is linked to an item.
    """
    file = models.FileField(_("file"))

    def __str__(self):
        return _("File '%s' in %s") % (self.file.url, self.item)


class Image(Data):
    """
    An image that is linked to an item.
    """
    file = ImageField(_("image"))

    def __str__(self):
        return _("Image '%s' in %s") % (self.file.url, self.item)
