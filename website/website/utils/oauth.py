from datetime import timedelta
import requests
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from django.utils.timezone import now


def ensure_valid_token(request, token: SocialToken):
    if token.expires_at and now() < token.expires_at:
        data = requests.get("https://oauth2.googleapis.com/tokeninfo", {"id_token": token.token}).json()
        if "error" not in data:
            return

    adapter: DefaultSocialAccountAdapter = get_adapter()
    app: SocialApp = adapter.get_app(request, token.app.provider, token.app.provider_id)  # type: ignore
    provider_id = app.provider_id or app.provider
    TOKEN_REFRESH_URLS = {"google": "https://oauth2.googleapis.com/token"}
    PARAMS = {
        "google": {
            "client_id": app.client_id,
            "client_secret": app.secret,
            "refresh_token": token.token_secret,
            "grant_type": "refresh_token",
        }
    }
    token_refresh_url = TOKEN_REFRESH_URLS.get(provider_id)
    params = PARAMS.get(provider_id)
    if not token_refresh_url or not params:
        return
    data = requests.post(token_refresh_url, params).json()
    if "error" in data:
        raise ValueError(f"{data.get('error', '')}: {data.get('error_description', '')}")
    token.token = data.get("access_token", "")
    expires_in = data.get("expires_in", None)
    if expires_in:
        token.expires_at = now() + timedelta(seconds=int(expires_in))
    token.save()
