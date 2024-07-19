from hashlib import md5
from pathlib import Path
import os.path
import posixpath
import re
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
    """A static files finder that uses the `TEMPLATES` setting to locate files."""

    def __init__(self):
        self.paths = {}
        self.storage = WebStorage(self.paths)

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
        # if it's not an URL, don't go further
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
                        self.files.append((get_name_from_url(url, self.paths), self.storage))

        if not self.files:
            self.files = None
            return []

        return self.files


class WebStorage(Storage):
    def __init__(self, paths: dict[str, str]):
        self.paths = paths

    def open(self, name, mode="rb"):
        if mode[0] == "w":
            raise ValueError("Can't write to a web file")
        name = self.paths.get(name, name)
        req = requests.get(name)
        return ContentFile(req.content if mode[-1] == "b" else req.text)

    def path(self, name):
        return name

def get_name_from_url(url, paths: dict[str, str] | None = None):
    # if it's not an URL, don't go further
    if not re.match(r"^[a-z]+:", url):
        return None

    parsed = urlparse(url)
    dir, basename = posixpath.split(parsed.path)
    basename, ext = posixpath.splitext(basename)
    dir = dir.strip("/")
    dir = f"/{dir}/" if dir else "/"

    if basename.endswith("css2"):
        ext += ".css"

    to_hash = parsed.query + parsed.fragment
    if to_hash:
        hasher = md5(usedforsecurity=False)
        hash = "." + hasher.hexdigest()[:4]
    else:
        hash = ""

    ret = f"ext/{parsed.hostname}{dir}{basename}{hash}{ext}"
    if paths is not None:
        paths[ret] = url
    return ret
