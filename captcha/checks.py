from captcha.constants import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY
from django.conf import settings
from django.core import checks


def recaptcha_key_check(*_args, **_kwargs):
    errors = []
    private_key = getattr(settings, "RECAPTCHA_PRIVATE_KEY", TEST_PRIVATE_KEY)
    public_key = getattr(settings, "RECAPTCHA_PUBLIC_KEY", TEST_PUBLIC_KEY)

    if not private_key or not public_key:
        errors.append(
            checks.Error(
                "RECAPTCHA_PRIVATE_KEY or RECAPTCHA_PUBLIC_KEY is empty.",
                id="captcha.recaptcha_key_empty",
            )
        )

    if not settings.TEST and (private_key == TEST_PRIVATE_KEY or public_key == TEST_PUBLIC_KEY):
        errors.append(
            checks.Warning(
                "RECAPTCHA_PRIVATE_KEY or RECAPTCHA_PUBLIC_KEY is making use of the Google test keys "
                "and will not behave as expected in a production environment",
                hint="Update settings.RECAPTCHA_PRIVATE_KEY and/or settings.RECAPTCHA_PUBLIC_KEY. "
                "Alternatively this check can be ignored by adding "
                "`SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']` to your settings file.",
                id="captcha.recaptcha_test_key_error",
            )
        )
    return errors
