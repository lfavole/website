import json
import time
from pathlib import Path

import jwt
import requests
from django.core.management.base import BaseCommand


# https://developers.google.com/identity/protocols/risc#auth_token
def make_bearer_token(credentials_file):
    with open(credentials_file) as service_json:
        service_account = json.load(service_json)
        issuer = service_account["client_email"]
        subject = service_account["client_email"]
        private_key_id = service_account["private_key_id"]
        private_key = service_account["private_key"]
    issued_at = int(time.time())
    expires_at = issued_at + 3600
    payload = {
        "iss": issuer,
        "sub": subject,
        "aud": "https://risc.googleapis.com/google.identity.risc.v1beta.RiscManagementService",
        "iat": issued_at,
        "exp": expires_at,
    }
    encoded = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": private_key_id})
    return encoded


# https://developers.google.com/identity/protocols/risc#config_stream
def configure_event_stream(auth_token, receiver_endpoint, events_requested):
    stream_update_endpoint = "https://risc.googleapis.com/v1beta/stream:update"
    headers = {"Authorization": "Bearer {}".format(auth_token)}
    stream_cfg = {
        "delivery": {
            "delivery_method": "https://schemas.openid.net/secevent/risc/delivery-method/push",
            "url": receiver_endpoint,
        },
        "events_requested": events_requested,
    }
    response = requests.post(stream_update_endpoint, json=stream_cfg, headers=headers)
    response.raise_for_status()  # Raise exception for unsuccessful requests


FOLDER = Path(__file__).parent.parent


class Command(BaseCommand):
    help = "Setup RISC on the corresponding Google app."

    def handle(self, **options):
        auth_token = make_bearer_token(options["path"])
        configure_event_stream(
            auth_token,
            f"https://{options['domain'].removeprefix('http://').removeprefix('https://')}/risc",
            [
                "https://schemas.openid.net/secevent/risc/event-type/sessions-revoked",
                "https://schemas.openid.net/secevent/oauth/event-type/tokens-revoked",
                "https://schemas.openid.net/secevent/oauth/event-type/token-revoked",
                "https://schemas.openid.net/secevent/risc/event-type/account-disabled",
                "https://schemas.openid.net/secevent/risc/event-type/account-enabled",
                "https://schemas.openid.net/secevent/risc/event-type/account-credential-change-required",
                "https://schemas.openid.net/secevent/risc/event-type/verification",
            ],
        )
        print("OK")

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="The path to the JSON service file.")
        parser.add_argument("--domain", required=True, help="The domain of the depolyed website.")
