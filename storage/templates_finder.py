from hashlib import md5
import mimetypes
from pathlib import Path
import os.path
import posixpath
import re
from typing import Literal, TypeVar, overload
from urllib.parse import urlparse
from django.conf import settings

from django.contrib.auth.models import AnonymousUser
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.http import HttpRequest
from django.template import RequestContext, loader
from django.templatetags.static import StaticNode
from django.utils._os import safe_join
import requests


class TemplatesFinder(BaseFinder):
    """A static files finder that uses the `TEMPLATES` setting to locate external files."""

    def __init__(self):
        self.storage = WebStorage()

        self.templates_dirs = []

        for engine in loader.engines.all():
            self.templates_dirs.extend(engine.template_dirs)

        self.templates = []
        for dir in self.templates_dirs:
            self.templates.extend(file for file in Path(dir).rglob("*") if not file.is_dir())

        self.files = []

    def check(self, **kwargs):
        return []

    def find(self, path, all=False):
        """Look for files."""
        # if it's an already processed URL, return it
        if path.startswith("ext/"):
            path = safe_join(settings.STATIC_ROOT, path)
            if os.path.exists(path):
                return [path] if all else path

        # get the target filename
        target_filename = get_name_from_url(path)
        # if it's not a URL, don't go further
        if target_filename is None:
            return []

        matches = []

        for filename, _storage in self.list():
            if filename == target_filename:
                if not all:
                    return filename
                matches.append(filename)

        return matches

    def list(self, _ignore_patterns=None):
        """List all files in all locations."""
        if self.files is None:
            return []
        if self.files:
            return self.files

        context = RequestContext(HttpRequest())
        context.request.user = AnonymousUser()

        for template in self.templates:
            parsed_template = loader.get_template(template)
            nodes: list[StaticNode] = parsed_template.template.nodelist.get_nodes_by_type(StaticNode)

            with context.bind_template(parsed_template.template):  # type: ignore
                for node in nodes:
                    url = node.path.resolve(context)  # type: ignore
                    if re.match(r"^[a-z]+:", url):
                        self.files.append((get_name_from_url(url), self.storage))

        if not self.files:
            self.files = None
            return []

        return self.files


class WebStorage(Storage):
    def open(self, name, mode="rb"):
        if mode[0] == "w":
            raise ValueError("Can't write to a web file")
        url = get_url_from_name(name)
        file = get_file_from_url(url, mode=mode) if url else None
        if file is None:
            raise ValueError(f"Invalid URL for WebStorage: {name}")
        return file

    def path(self, name):
        return get_url_from_name(name)


_names: dict[str, str] = {}
_files: dict[str, ContentFile] = {}


class EmptyContentFileMeta(type):
    def __instancecheck__(self, instance):
        return instance.size == 0


class EmptyContentFile(ContentFile, metaclass=EmptyContentFileMeta):
    size: Literal[0]


@overload
def get_file_from_url(url: str, req_method: str = "GET", mode: str = "rb") -> ContentFile | None:
    pass


@overload
def get_file_from_url(url: str, req_method: Literal["HEAD"], mode: str = "rb") -> EmptyContentFile | None:
    pass


def get_file_from_url(url: str, req_method="GET", mode="rb"):
    """
    Returns a `ContentFile` that comes from a URL with a name that can be used on the local file system.

    If the method is HEAD, the request will be made only if needed and the content will not be available.
    """
    # if it's not a URL, don't go further
    if not re.match(r"^[a-z]+://", url):
        return None

    # if a file has already been fetched, return it
    if url in _files:
        return _files[url]

    # if we only ask for the filename and the name is available, immediatly return an empty file
    if req_method == "HEAD" and url in _names:
        return ContentFile(b"", _names[url])

    parsed = urlparse(url)
    dir, basename = posixpath.split(parsed.path)
    basename, ext = posixpath.splitext(basename)
    # fix redundant slashes in the directory name
    dir = dir.strip("/")
    if dir:
        dir += "/"

    req = None
    # do the request now if we don't use the HEAD method
    if req_method != "HEAD":
        try:
            req = req or requests.request(req_method, url)
        except ValueError:
            # skip data, ftp... URLs
            return None

    # add an extension to avoid bugs with the X-Content-Type-Options: nosniff header
    if not ext:
        if basename.endswith("css2"):
            ext += ".css"
        elif basename.endswith("+esm"):
            ext += ".js"
        else:
            # use the Content-Type header to get the extension
            try:
                req = req or requests.head(url)
            except ValueError:
                # skip data, ftp... URLs
                pass
            else:
                ext_suffix = mimetypes.guess_extension(req.headers.get("Content-Type", "").split(";")[0])
                if ext_suffix:
                    ext += ext_suffix

    # hash the query string and the fragment if there are any
    to_hash = parsed.query + parsed.fragment
    if to_hash:
        hasher = md5(usedforsecurity=False)
        hash = "." + hasher.hexdigest()[:4]
    else:
        hash = ""

    # build and cache the final name
    # skip the parts that are not present
    name = f"ext/{(parsed.hostname + '/') if parsed.hostname else ''}{dir}{basename}{hash}{ext}"
    _names[url] = name

    # store the file, except for the HEAD method
    if req_method != "HEAD":
        file = ContentFile(req.content if mode[-1] == "b" else req.text, name)  # type: ignore
        _files[url] = file
        return file

    return ContentFile(b"", name)


def get_name_from_url(url: str):
    """Return a file name that corresponds to a URL."""
    ret = get_file_from_url(url, "HEAD")
    if not ret:
        return None
    return ret.name


T = TypeVar("T")


def get_url_from_name(target_name: str, default: T = None) -> str | T:
    """Return a URL that corresponds to a file name."""
    for url, name in _names.items():
        if name == target_name:
            return url
    return default


def get_file_from_name(target_name: str, default: T = None) -> ContentFile | T:
    """Return a `ContentFile` that corresponds to a file name."""
    url = get_url_from_name(target_name)
    if url is None:
        return default
    return _files.get(url, default)
