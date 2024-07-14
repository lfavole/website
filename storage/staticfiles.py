import os.path
import sys

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.files.base import ContentFile



class CustomStaticFilesStorage(ManifestStaticFilesStorage):
    support_js_module_import_aggregation = True

    def compress_picture(self, name):
        try:
            from PIL import Image
        except ImportError:
            return

        with self.open(name) as f:
            try:
                img = Image.open(f)
            except (ValueError, OSError):
                return

            content_file = ContentFile(b"")
            img.save(content_file, img.format)

        return self._save(name, content_file)  # type: ignore

    def minify(self, name):
        try:
            import minify_html
        except ImportError:
            return

        prefix = {".css": "<style>", ".js": "<script>"}.get(os.path.splitext(name)[1])
        if prefix is None:
            return

        with self.open(name) as f:
            if hasattr(f, "seek"):
                f.seek(0)
            try:
                content = f.read().decode("utf-8")
            except UnicodeDecodeError:
                return

        if self.exists(name):
            self.delete(name)

        try:
            content = minify_html.minify(
                prefix + content,
                minify_css=True,
                minify_js=True,
                do_not_minify_doctype=True,
            ).removeprefix(prefix)
        except:
            pass

        content_file = ContentFile(content.encode())
        return self._save(name, content_file)  # type: ignore

    def process(self, name):
        return self.minify(name) or self.compress_picture(name)

    def post_process(self, paths, dry_run=False, **options):
        if dry_run:
            return

        for name, hashed_name, processed in super().post_process(paths, dry_run, **options):
            data = self.process(hashed_name if processed else name)
            if data:
                hashed_name = data
                processed = True

            yield name, hashed_name, processed

    def _url(self, hashed_name_func, name, force=False, hashed_files=None):
        if "runserver" not in sys.argv:
            force = True
        return super()._url(hashed_name_func, name, force, hashed_files)
