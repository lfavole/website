import os.path

from django.db import models
from easy_thumbnails.engine import NoSourceGenerator
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.fields import ThumbnailerField
from easy_thumbnails.files import Thumbnailer, ThumbnailerFieldFile

from .widgets import CustomImageClearableFileInput


class FileField(ThumbnailerField):
    """
    File field class for compressing all the incoming images.
    """

    def __init__(self, *args, **kwargs):
        self.resize_source = kwargs.pop("resize_source", (1920, 1080))
        super().__init__(*args, **kwargs)

    def pre_save(self, *args, **kwargs):
        file: ThumbnailerFieldFile = super(models.FileField, self).pre_save(*args, **kwargs)
        if file._committed or os.path.splitext(file.name)[1] == ".svg":  # don't rasterize SVGs
            return file

        thumbnailer = Thumbnailer(file)
        thumbnailer.thumbnail_namer = self.thumbnail_namer  # type: ignore
        try:
            thumbnail = thumbnailer.generate_thumbnail({"size": self.resize_source, "autocrop": True})
        except (InvalidImageFormatError, NoSourceGenerator):
            if file and not file._committed:
                file.save(file.name, file.file, save=False)
            return file

        if thumbnail:
            committed = file._committed
            file = ThumbnailerFieldFile(file.instance, self, thumbnail.name)
            file.file = thumbnail.file
            file._committed = committed

        if file and not file._committed:
            file.save(file.name, file.file, save=False)

        return file

    @staticmethod
    def thumbnail_namer(source_filename, thumbnail_extension, **kwargs):
        """
        Return the name of the compressed image.
        """
        return os.path.splitext(source_filename)[0] + "." + thumbnail_extension


class ImageField(FileField, models.ImageField):
    """
    Image class for compressing all the incoming images.
    """

    def formfield(self, **kwargs):
        del kwargs["widget"]
        return super().formfield(**{"widget": CustomImageClearableFileInput, "max_length": self.max_length, **kwargs})
