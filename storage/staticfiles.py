import fnmatch
from io import BytesIO
import os.path
import posixpath
import re
import sys

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.files.base import ContentFile
import requests

from .templates_finder import get_name_from_url


class CustomStaticFilesStorage(ManifestStaticFilesStorage):
    support_js_module_import_aggregation = True
    _js_module_import_aggregation_patterns = (
        "*.js",
        (
            (
                r"""(?P<matched>import(?P<import>[\s\{].*?)\s*from\s*['"](?P<url>.*?)["']\s*;)""",
                """import%(import)s from "%(url)s";""",
            ),
            (
                (r"""(?P<matched>export(?s:(?P<exports>[\s\{].*?))""" r"""\s*from\s*["'](?P<url>.*?)["']\s*;)"""),
                """export%(exports)s from "%(url)s";""",
            ),
            (
                r"""(?P<matched>import\s*['"](?P<url>.*?)["']\s*;)""",
                """import"%(url)s";""",
            ),
            (
                r"""(?P<matched>import\(["'](?P<url>.*?)["']\))""",
                """import("%(url)s")""",
            ),
        ),
    )
    manifest_strict = False

    def fetch_external(self, name, content, files):
        try:
            data = content.decode("utf-8")
        except UnicodeDecodeError:
            return content

        for pattern, repls in self._patterns.items():  # type: ignore
            if not fnmatch.fnmatchcase(name, pattern):
                continue
            for regex, repl in repls:

                def replace(match):
                    nonlocal repl

                    url = match["url"]
                    # if it's not an external URL, stop here
                    if not re.match(r"^[a-z]+:", url):
                        return match[0]

                    try:
                        req = requests.get(url)
                    except requests.exceptions.InvalidSchema:
                        # skip data, ftp... URLs
                        return match[0]

                    file = ContentFile(req.content)
                    filepath = self.save(self.hashed_name(get_name_from_url(url), file), file)  # type: ignore
                    files.append((filepath, filepath, True))

                    url = posixpath.relpath(name, os.path.dirname(filepath))

                    return repl % {"url": url}  # pylint: disable=W0640

                regex.sub(replace, data)

        return content

    def compress_picture(self, _name, content):
        try:
            from PIL import Image
        except ImportError:
            return None

        try:
            img = Image.open(BytesIO(content))
        except (ValueError, OSError):
            return None

        output = BytesIO()
        img.save(output, img.format)
        output.seek(0)
        return output.read()

    def minify(self, name, content):
        try:
            import minify_html
        except ImportError:
            return content

        prefix = {".css": "<style>", ".js": "<script>"}.get(os.path.splitext(name)[1])
        if prefix is None:
            return content

        try:
            data = content.decode("utf-8")
        except UnicodeDecodeError:
            return content

        try:
            return (
                minify_html.minify(
                    prefix + data,
                    minify_css=True,
                    minify_js=True,
                    do_not_minify_doctype=True,
                )
                .removeprefix(prefix)
                .encode()
            )
        except:
            return content

    def process(self, name, files):
        with self.open(name) as f:
            if hasattr(f, "seek"):
                f.seek(0)
            content = f.read()
            content = self.fetch_external(name, content, files)
            content = self.minify(name, content)
            content = self.compress_picture(name, content)
            if not content:
                return name

            if self.exists(name):
                self.delete(name)
            content_file = ContentFile(content)
            return self._save(name, content_file)  # type: ignore

    def post_process(self, paths, dry_run=False, **options):  # pylint: disable=W0221
        if dry_run:
            return

        files = [*super().post_process(paths, dry_run, **options)]
        for name, hashed_name, processed in files:
            data = self.process(hashed_name if processed else name, files)
            if data:
                hashed_name = data
                processed = True

            yield name, hashed_name, processed

    def _url(self, hashed_name_func, name, force=False, hashed_files=None):
        if "runserver" not in sys.argv:
            force = True

        # return the URL as is during debug
        if re.match(r"^[a-z]+:", name) and not force:
            return name

        # otherwise, change the path for external URLs
        return super()._url(  # type: ignore
            hashed_name_func,
            (get_name_from_url(name) if force else "") or name,
            force,
            hashed_files,
        )
