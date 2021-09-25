import logging
import os
import urllib.parse

from endpoint.base import BaseHandler
from PIL import ExifTags, Image
from lib.models import Picture, PictureSchema
from tornado import gen
from tornado.web import stream_request_body

MAX_STREAMED_SIZE = 12 * 1024 * 1024  # 12Mo

picture_schema = PictureSchema()

@stream_request_body
class UploadHandler(BaseHandler):
    @gen.coroutine
    def prepare(self):
        yield super().prepare()

        self.filename = urllib.parse.unquote(self.path_kwargs["filename"])
        self.file_path = os.path.join(self.external_path, self.filename)
        self.request.connection.set_max_body_size(MAX_STREAMED_SIZE)

    def data_received(self, chunk):
        with open(self.file_path, "ab") as file:
            file.write(chunk)

    @gen.coroutine
    def post(self, filename):
        """PUT External Picture"""
        self.action_name = "PostPicture"

        thumbnail_path = os.path.join(self.thumbnails_path, self.filename)
        picture = self.pm.addPicture(filename, self.file_path, thumbnail_path)
        yield self.resize_picture()

        yield self.application.send_msg_to_websockets(
            {
                "event": "update",
                "type": "state",
                "mutation": "pictures/newPictures",
                "value": picture_schema.dump(picture),
            }
        )

        self.finish()

    @gen.coroutine
    def resize_picture(self):
        image = Image.open(self.file_path)
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
            logging.error(exc)
            logging.info("pictures does not have exif for orientation")

        image.thumbnail(size)
        photo_thumb_path = os.path.join(self.thumbnails_path, self.filename)

        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")
        image.save(photo_thumb_path, "JPEG")
        return photo_thumb_path
