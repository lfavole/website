from django.core.files.storage import FileSystemStorage

from .blob import BlobFileStorage
from .filename_hash import FilenameHashMixin
from .templates_finder import get_name_from_url


class CustomFileSystemStorage(FilenameHashMixin, FileSystemStorage):
    """
    Custom filesystem storage that adds a random hash to every created filename.
    """

    def path(self, name):
        return super().path(get_name_from_url(name) or name)


class CustomBlobStorage(FilenameHashMixin, BlobFileStorage):
    """
    Custom Vercel Blob storage that adds a random hash to every created filename.
    """
