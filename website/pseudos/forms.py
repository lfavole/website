from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class PseudosForm(forms.Form):
    words = forms.CharField(
        label=_("words"),
        widget=forms.Textarea(attrs={"rows": "10", "placeholder": _("1 word per line\nWrite your name for example")}),
        help_text=_("The synonyms of these words will be included") if not settings.PYTHONANYWHERE else "",
    )
    syllables_n = forms.IntegerField(
        label=_("syllables number"),
        initial=4,
        validators=[MinValueValidator(1)],
    )
    words_n = forms.IntegerField(
        label=_("names number"),
        initial=10,
        validators=[MinValueValidator(0)],
        help_text=_("0 for listing all the possibilities"),
    )
