from captcha.constants import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY
from django.conf import settings
from django.core import checks


def hcaptcha_key_check(*_args, **_kwargs):
    errors = []
    private_key = getattr(settings, "HCAPTCHA_PRIVATE_KEY", TEST_PRIVATE_KEY)
    public_key = getattr(settings, "HCAPTCHA_PUBLIC_KEY", TEST_PUBLIC_KEY)

    if not private_key or not public_key:
        errors.append(
            checks.Error(
                "HCAPTCHA_PRIVATE_KEY or HCAPTCHA_PUBLIC_KEY is empty.",
                id="captcha.hcaptcha_key_empty",
            )
        )

    if not settings.TEST and (private_key == TEST_PRIVATE_KEY or public_key == TEST_PUBLIC_KEY):
        errors.append(
            checks.Warning(
                "HCAPTCHA_PRIVATE_KEY or HCAPTCHA_PUBLIC_KEY is making use of the hCaptcha test keys "
                "and will not behave as expected in a production environment",
                hint="Update settings.HCAPTCHA_PRIVATE_KEY and/or settings.HCAPTCHA_PUBLIC_KEY. "
                "Alternatively this check can be ignored by adding "
                "`SILENCED_SYSTEM_CHECKS = ['captcha.hcaptcha_test_key_error']` to your settings file.",
                id="captcha.hcaptcha_test_key_error",
            )
        )
    return errors
