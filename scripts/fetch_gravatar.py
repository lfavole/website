import hashlib
import os
from pathlib import Path

import requests

SIZE_BIG = 100
SIZE_SMALL = 16
EMAIL = "laurentfavole03@gmail.com"


def main(_args=None, reloading=False):
    print("Fetching Gravatar")
    md5 = hashlib.md5(EMAIL.encode("utf-8")).hexdigest()

    for size in (SIZE_BIG, SIZE_SMALL):
        print(f"Downloading image ({size}px)")
        req = requests.get(f"https://www.gravatar.com/avatar/{md5}?s={size}", stream=True)
        suffix = "" if size == SIZE_BIG else f"_{size}"
        path = Path(__file__).resolve().parent.parent / f"data/static/global/profile{suffix}.jpg"
        if not path.parent.exists():
            os.makedirs(path.parent)
        with path.open("wb") as f:
            for data in req.iter_content(chunk_size=64 * 1024):
                f.write(data)

    if not reloading:
        from .reload import main as reload

        reload()


def contribute_to_argparse(_parser):
    pass
