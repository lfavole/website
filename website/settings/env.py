import os
import re
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

TEST = os.environ.get("TEST")

PYTHONANYWHERE = bool(os.environ.get("PYTHONANYWHERE"))
VERCEL = bool(os.environ.get("VERCEL"))

DEVELOPMENT = bool(int(os.getenv("DEVELOPMENT", "0")))
if DEVELOPMENT:
    PRODUCTION = False
else:
    PRODUCTION = PYTHONANYWHERE or VERCEL or bool(int(os.environ.get("PRODUCTION", "0")))

OFFLINE = False if PYTHONANYWHERE or VERCEL else os.environ.get("OFFLINE")

GITHUB_REPO = os.environ.get("GITHUB_REPO")
GITHUB_WEBHOOK_KEY = os.environ.get("GITHUB_WEBHOOK_KEY")

DEBUG = bool(int(os.environ.get("DEBUG") or 0))

# Sentry

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_SDK = None

match = re.match(r"^https?://(\w+)(?:@\w+)?\.ingest(?:\.([a-z]+))?\.sentry\.io/", SENTRY_DSN)
if match:
    SENTRY_SDK = f"https://js{'-' + match[2] if match[2] else ''}.sentry-cdn.com/{match[1]}.min.js"
