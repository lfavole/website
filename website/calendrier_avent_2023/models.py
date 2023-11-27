from django.urls import reverse
from blog.models import Image
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from website.templatetags.format_day import format_day, format_day_html


class Day(models.Model):
    day = models.IntegerField(_("day"), unique=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name=_("image"))

    class Meta:
        verbose_name = _("Day")

    def __str__(self):
        return mark_safe(format_day(self.day) + " décembre")

    def __html__(self):
        return mark_safe(format_day_html(self.day) + " décembre")

    def get_absolute_url(self):
        return reverse("calendrier_avent_2023:day", args=[self.day])
