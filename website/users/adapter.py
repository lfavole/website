from allauth.mfa.adapter import DefaultMFAAdapter
from allauth.account.adapter import DefaultAccountAdapter


class Adapter(DefaultMFAAdapter, DefaultAccountAdapter):
    pass
