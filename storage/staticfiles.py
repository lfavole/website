import fnmatch
from io import BytesIO
import os.path
import posixpath
import re
import sys
from urllib.parse import urljoin
from django.conf import settings

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.files.base import ContentFile
from django.utils.html import escapejs

from .templates_finder import get_name_from_url, get_file_from_url, get_url_from_name


class CustomStaticFilesStorage(ManifestStaticFilesStorage):
    support_js_module_import_aggregation = True
    # fix the patterns to allow external URLs
    _js_module_import_aggregation_patterns = (
        "*.js",
        (
            (
                r"""(?P<matched>import(?P<import>[\s\{].*?)\s*from\s*['"](?P<url>[./\w].*?)["']\s*;)""",
                """import%(import)s from "%(url)s";""",
            ),
            (
                (r"""(?P<matched>export(?:(?P<exports>[\s\{].*?))""" r"""\s*from\s*["'](?P<url>[./\w].*?)["']\s*;)"""),
                """export%(exports)s from "%(url)s";""",
            ),
            (
                r"""(?P<matched>import\s*['"](?P<url>[./\w].*?)["']\s*;)""",
                """import"%(url)s";""",
            ),
            (
                r"""(?P<matched>import\(["'](?P<url>[./\w].*?)["']\))""",
                """import("%(url)s")""",
            ),
        ),
    )
    manifest_strict = False

    def add_sentry_dsn(self, _name, content):
        """Add the Sentry DSN to the `sentry.js` file."""
        SENTRY_DSN = settings.SENTRY_DSN
        if not SENTRY_DSN:
            return content

        try:
            data = content.decode("utf-8")
        except UnicodeDecodeError:
            return content

        data = re.sub(r'dsn: ?"[^"]*?"', f'dsn: "{escapejs(SENTRY_DSN)}"', data)
        return data.encode("utf-8")

    def fetch_external(self, name, initial_name, content, files):
        """
        Search for external links, download the corresponding files and
        change the URL to make it point to the local file.

        Also add the downloaded files to the processing queue.
        """
        try:
            data = content.decode("utf-8")
        except UnicodeDecodeError:
            return content

        for pattern, repls in self._patterns.items():  # type: ignore
            if not fnmatch.fnmatchcase(name, pattern):
                continue
            for regex, repl in repls:

                def replace(match: re.Match):
                    url = match["url"]

                    base_path = get_url_from_name(initial_name, initial_name)
                    url = urljoin(base_path, url)  # type: ignore

                    file = get_file_from_url(url, "GET")
                    if file is None:
                        # skip data, ftp... URLs or erroneous URLs (like local files)
                        return match[0]

                    # save the file and change the file name
                    # don't process a file multiple times (if it is referenced from multiple locations)
                    if not getattr(file, "processed", False):
                        file.name = self.save(self.hashed_name(file.name, file), file)  # type: ignore
                        file.processed = True  # type: ignore

                    # add the file to the queue if it's not already there
                    for file_to_check in files:
                        if file_to_check[0] == url:
                            break
                    else:
                        files.append((url, file.name, True))

                    # build a relative URL for the file
                    url = posixpath.relpath(file.name, os.path.dirname(name))

                    # make the URL replacement
                    return repl % {**match.groupdict(), "url": url}  # pylint: disable=W0640

                data = regex.sub(replace, data)

        return data.encode("utf-8")

    def compress_picture(self, _name, content):
        """Re-save all pictures and compress them."""
        try:
            from PIL import Image
        except ImportError:
            return content

        try:
            img = Image.open(BytesIO(content))
        except (ValueError, OSError):
            return content

        output = BytesIO()
        img.save(output, img.format)
        output.seek(0)
        return output.read()

    def minify(self, name, content):
        """Minify CSS and JavaScript files."""
        try:
            import minify_html
        except ImportError:
            # stop here if the minifier is not available
            return content

        prefix = {".css": "<style>", ".js": "<script>"}.get(os.path.splitext(name)[1])
        if prefix is None:
            return content

        try:
            data = content.decode("utf-8")
        except UnicodeDecodeError:
            return content

        try:
            # minify by creating a fake HTML tag and removing it
            return (
                minify_html.minify(
                    prefix + data,
                    minify_css=True,
                    minify_js=True,
                    minify_doctype=False,
                )
                .removeprefix(prefix)
                .encode("utf-8")
            )
        except:
            # skip all errors (but they are still displayed to the console)
            return content

    def process(self, name, initial_name, files):
        """Process a static file."""
        with self.open(name) as f:
            if hasattr(f, "seek"):
                f.seek(0)
            content = f.read()
            content = self.add_sentry_dsn(name, content)
            content = self.fetch_external(name, initial_name, content, files)
            # content = self.minify(name, content)
            content = self.compress_picture(name, content)

            if self.exists(name):
                self.delete(name)
            content_file = ContentFile(content)
            return self._save(name, content_file)  # type: ignore

    def post_process(self, paths, dry_run=False, **options):  # pylint: disable=W0221
        if dry_run:
            return

        files = [*super().post_process(paths, dry_run, **options)]
        for name, hashed_name, processed in files:
            hashed_name = self.process(hashed_name if processed else name, name, files)
            processed = True

            yield name, hashed_name, processed

    def _url(self, _hashed_name_func, name, force=False, hashed_files=None):
        if "runserver" not in sys.argv:
            force = True

        # return the URL as is during debug
        if re.match(r"^[a-z]+:", name) and not force:
            return name

        # otherwise, change the path for external URLs
        return super()._url(  # type: ignore
            self._stored_name if hashed_files is not None else self.stored_name,  # type: ignore
            (get_name_from_url(name) if force else "") or name,
            force,
            hashed_files,
        )

    def stored_name(self, name):
        if get_name_from_url(name):
            # don't hash URLs
            return name
        return super().stored_name(name)

    def path(self, name):
        url_name = get_name_from_url(name)
        if url_name:
            # try to get the hashed file
            try:
                return super().path(self.stored_name(url_name))
            except ValueError:
                pass
        return super().path(name)
