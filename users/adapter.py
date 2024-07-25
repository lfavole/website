from allauth.account import views
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.models import SocialApp
from django.shortcuts import resolve_url


class Adapter(DefaultAccountAdapter):
    """Dummy adapter."""


class CustomLoginView(views.LoginView):
    """Login view that adds parameters for One Tap sign-in."""

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)

        # pass settings to the template for One Tap sign-in
        try:
            adapter: DefaultSocialAccountAdapter = get_adapter()
            app: SocialApp = adapter.get_app(self.request, "google")  # type: ignore
            ret["GOOGLE_CLIENT_ID"] = app.client_id
        except SocialApp.DoesNotExist:
            pass

        ret["GOOGLE_REDIRECT_URI"] = self.request.build_absolute_uri(resolve_url("google_login_by_token"))

        return ret


views.login = CustomLoginView.as_view()
