import datetime as dt
import os
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
import requests


@deconstructible
class BlobFileStorage(Storage):
    def __init__(self, folder="", token=None):
        self.folder = folder.rstrip("/")
        if self.folder:
            self.folder += "/"
        self._prefix = None
        self._token = token or os.environ.get("BLOB_READ_WRITE_TOKEN")
        if not self._token:
            raise ValueError("A token is required to use BlobFileStorage")

    def _request(self, method, url, *, data=None, json=None, headers=None):
        headers = {
            "Authorization": f"Bearer {self._token}",
            "X-API-Version": "7",
            **(headers or {}),
        }
        params = None
        if method == "GET":
            params = data
            data = None
        resp = requests.request(
            method,
            f"https://blob.vercel-storage.com/{url}",
            params=params,
            data=data,
            json=json,
            headers=headers,
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError as err:
            raise requests.HTTPError(resp.text) from err
        return resp.json()

    def delete(self, name):
        self._request("POST", "delete", json={"urls": [self.folder + name]})

    def exists(self, name):
        try:
            self.url(name)
            return True
        except FileNotFoundError:
            return False

    def listdir(self, path):
        data = self._request("GET", "", data={"prefix": self.folder + path.rstrip("/") + "/", "mode": "folded"})
        return data["folders"], [file["pathname"] for file in data["blobs"]]

    def size(self, name):
        data = self._request("GET", "", data={"url": self.url(name)})
        return data["size"]

    def get_info(self, name):
        """Return information about a blob as provided by the Vercel API."""
        name = name or ""

        data = self._request("GET", "", data={"prefix": self.folder + name})
        if not data["blobs"]:
            raise FileNotFoundError(f"The file {name} doesn't exist")

        self._prefix = data["blobs"][0]["url"].removeprefix(name).rstrip("/").removeprefix(self.folder).rstrip("/")
        return data["blobs"][0]

    def url(self, name):
        if self._prefix:
            return f"{self._prefix}{self.folder}/{name}"

        return self.get_info(name)["url"]

    def save(self, name, content, max_length=None):
        name = self.get_available_name(name, max_length)  # type: ignore
        self._request("PUT", self.folder + name, data=content.read(), headers={"X-Add-Random-Suffix": "false"})
        return name

    def get_created_time(self, name):
        return dt.datetime.fromisoformat(self.get_info(name)["uploadedAt"])

    get_accessed_time = get_created_time
    get_modified_time = get_created_time
