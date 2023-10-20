from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from globals.models import BasePage
from storage.fields import ImageField


class Page(BasePage):
    """
    A blog page.
    """

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
