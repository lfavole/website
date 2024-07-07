import hashlib
from pathlib import Path

import requests
from django.core.management.base import BaseCommand

SIZE_BIG = 100
SIZE_SMALL = 16
EMAIL = "laurentfavole03@gmail.com"


class Command(BaseCommand):
    def handle(self, reloading=False, **_options):
        print("Fetching Gravatar")
        md5 = hashlib.md5(EMAIL.encode("utf-8")).hexdigest()

        for size in (SIZE_BIG, SIZE_SMALL):
            print(f"Downloading image ({size}px)")
            req = requests.get(f"https://www.gravatar.com/avatar/{md5}?s={size}", stream=True)
            path = Path(__file__).resolve().parent.parent / f"data/static/global/profile_{size}.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as f:
                for data in req.iter_content(chunk_size=64 * 1024):
                    f.write(data)

        if not reloading:
            from .reload import Command as Reload

            Reload()
