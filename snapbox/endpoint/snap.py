import json
import logging
import os

from decorators import block_external_call
from endpoint.base import BaseHandler
from lib.models import PictureSchema
from PIL import ExifTags, Image
from tornado import gen

picture_schema = PictureSchema()


class SnapHandler(BaseHandler):
    @gen.coroutine
    @block_external_call
    def get(self):
        logging.debug("do_capture")

        picture = self.camera.capture_image()
        filename = os.path.basename(picture.path)
        yield self.generate_thumbnail(filename, picture.path)

        dump = picture_schema.dump(picture)
        self.write(json.dumps(dump))

    @gen.coroutine
    def generate_thumbnail(self, filename, path):
        image = Image.open(path)
        max_width = 840
        max_height = 560
        size = max_width, max_height

        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            exif = dict(image._getexif().items())

            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        except Exception as exc:
            logging.info("pictures does not have exif for orientation")
            logging.error(exc)

        image.thumbnail(size)
        photo_thumb_path = os.path.join(self.thumbnails_path, filename)

        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")
        image.save(photo_thumb_path, "JPEG")
        return photo_thumb_path
