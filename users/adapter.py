from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import DefaultMFAAdapter


class Adapter(DefaultMFAAdapter, DefaultAccountAdapter):
    error_messages = {
        **DefaultMFAAdapter.error_messages,
        **DefaultAccountAdapter.error_messages,
    }
