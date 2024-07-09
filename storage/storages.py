import os.path
from pathlib import PurePath

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.files.utils import validate_file_name
from django.utils.crypto import get_random_string
from django.utils.functional import keep_lazy_text

from website.utils.text import slugify


@keep_lazy_text
def get_valid_filename(filename: str):
    """
    Get a valid filename from the given filename.
    """
    name, ext = os.path.splitext(filename)
    name = slugify(name)
    ext = slugify(ext)
    filename = name + ext
    if not filename:
        raise SuspiciousFileOperation(f"Could not derive file name from '{filename}'")
    return filename


class CustomFileSystemStorage(FileSystemStorage):
    """
    Custom filesystem storage that uses a custom filename generator.
    """

    def get_valid_name(self, name: str):
        return get_valid_filename(name)

    def get_alternative_name(self, file_root: str, file_ext: str):
        file_root = get_valid_filename(file_root)
        hash_length = 8
        hash_chars = "0123456789abcdef"
        hash = os.path.splitext(file_root)[1][1:]
        if len(hash) == hash_length and all(char in hash_chars for char in hash):
            # remove the existing hash
            file_root = file_root[0 : -len(hash) - 1]
        return f"{file_root}.{get_random_string(hash_length, hash_chars)}{file_ext}"

    def splitext(self, name: str):
        root, ext = os.path.splitext(name)
        root, hash = os.path.splitext(root)
        return root, hash[1:], ext

    def get_available_name(self, name, max_length: int | None = None):
        """
        Return a filename that's free on the target storage system and
        available for new content to be written to.
        """
        name = str(name).replace("\\", "/")
        dir_name, file_name = os.path.split(name)
        if ".." in PurePath(dir_name).parts:
            raise SuspiciousFileOperation(f"Detected path traversal attempt in '{dir_name}'")

        validate_file_name(file_name)
        # pass the filename to get_alternative_name to have a hash
        file_name = self.get_alternative_name(*os.path.splitext(file_name))
        name = os.path.join(dir_name, file_name)
        file_root, file_hash, file_ext = self.splitext(file_name)

        # If the filename already exists, generate an alternative filename until it doesn't exist.
        # Truncate original name (without the hash) if required, so the new filename does not exceed the max_length.
        while self.exists(name) or (max_length and len(name) > max_length):
            # file_ext includes the dot.
            name = os.path.join(dir_name, self.get_alternative_name(file_root + "." + file_hash, file_ext))
            if max_length is None:
                continue

            # Truncate file_root if max_length exceeded.
            truncation = len(name) - max_length
            if truncation > 0:
                file_root = file_root[:-truncation]
                # Entire file_root was truncated in attempt to find an available filename.
                if not file_root:
                    raise SuspiciousFileOperation(
                        f'Storage can not find an available filename for "{name}" because '
                        f'the "max_length" of the field is {max_length}.'
                    )
                name = os.path.join(dir_name, self.get_alternative_name(file_root + "." + file_hash, file_ext))

        return name


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
