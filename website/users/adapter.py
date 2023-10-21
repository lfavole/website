from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import DefaultMFAAdapter


class Adapter(DefaultMFAAdapter, DefaultAccountAdapter):
    pass
