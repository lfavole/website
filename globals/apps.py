from django.apps import AppConfig
from django.core.mail import mail_managers
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django_comments.signals import comment_was_flagged


class GlobalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "globals"
    verbose_name = _("Global configuration")


@receiver(comment_was_flagged)
def send_flag_email(flag, created, **_kwargs):
    """Send an email to the `MANAGERS` when a comment is flagged."""
    if not created:
        return
    mail_managers(
        _("A comment was flagged"),
        render_to_string(
            "account/email/comment_flagged_message.txt",
            {"comment": flag.comment, "flag": flag},
        ),
    )
