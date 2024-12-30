import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class AuthorizedDelivering(models.Model):
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, unique=True)
    recipient = models.CharField(_("Recipient"), max_length=255)
    description = models.CharField(_("Description"), max_length=255, blank=True)

    def __str__(self):
        return self.description
