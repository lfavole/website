import io
import re

import requests
from django.http.response import HttpResponse

import custom_settings

callbacks = []


def pattern(test):
    def wrapper(f):
        callbacks.append((test, f))
        return f

    return wrapper


BOT_TOKEN = custom_settings.BOT_TOKEN
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def call_api(method, endpoint, params=None, *args, **kwargs):
    if not BOT_TOKEN:
        return None
    return requests.request(method, BASE_URL + "/" + endpoint, *args, params=params, **kwargs)


def reply(request):
    req = call_api("GET", "getUpdates")
    if req is None:
        return None
    data = req.json()

    for update in data["result"]:
        message = update["message"]
        text = message.get("text", "")
        for callback in callbacks:
            test = callback[0]
            if isinstance(test, str):
                if test != text:
                    continue
            elif isinstance(test, re.Pattern):
                if not test.search(text):
                    continue
            else:
                if not test(message):
                    continue
            callback[1](message)
            break

    rem = 0
    if len(data["result"]) > 0:
        offset = data["result"][-1]["update_id"] + 1
        req2 = call_api("GET", "getUpdates", {"offset": offset})
        data2 = req2.json()
        rem = len(data2["result"])
    return HttpResponse(f"{len(data['result'])} messages answered, {rem} remaining")


@pattern("/image")
def _(message):
    from PIL import Image

    img = Image.new("RGB", (1920, 1080))
    for x in range(1920):
        for y in range(1080):
            color = (255, 255, 255) if (x + y) % 100 < 50 else (0, 0, 0)
            img.putpixel((x, y), color)

    output = io.BytesIO()
    img.save(output, format="jpeg")
    output.seek(0)
    call_api(
        "POST",
        "sendPhoto",
        {
            "chat_id": message["from"]["id"],
            "text": "Vous avez dit : " + message["text"],
        },
        files={"photo": output},
    )


@pattern("/fractal")
def _(message):
    call_api(
        "POST",
        "sendPhoto",
        {
            "chat_id": message["from"]["id"],
            "photo": "https://mandelbrowser.y0.pl/tutorial/images/julia.png",
            "text": "Vous avez dit : " + message["text"],
        },
    )


@pattern(lambda text: True)
def _(message):
    call_api("POST", "sendMessage", {"chat_id": message["from"]["id"], "text": "Vous avez dit : " + message["text"]})
