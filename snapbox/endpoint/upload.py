import logging

import tornado.web
from tornado import iostream, gen
from tornado.web import stream_request_body, HTTPError
import urllib.parse
import hashlib
import json
import os

from PIL import Image, ExifTags

from endpoint.base import BaseHandler

from lib.models import Picture, PictureSchema

picture_schema = PictureSchema()
pictures_schema = PictureSchema(many=True)

MAX_STREAMED_SIZE = 12 * 1024 * 1024 # 12Mo

@stream_request_body
class UploadHandler(BaseHandler):

    @gen.coroutine
    def prepare(self):
        yield super().prepare()

        self.filename = urllib.parse.unquote(self.path_kwargs['filename'])
        print('filename : [%s]' % self.filename)
        print('external_path : [%s]' % self.external_path)
        self.file_path = os.path.join(self.external_path, self.filename)
        print(self.file_path)

        self.request.connection.set_max_body_size(MAX_STREAMED_SIZE)

    def data_received(self, chunk):
        with open(self.file_path, 'ab') as file:
            file.write(chunk)

    @gen.coroutine
    def post(self, filename):
        """ PUT External Picture """
        self.action_name = 'PostPicture'

        thumbnail_path = os.path.join(self.thumbnails_path, self.filename)
        self.pm.addPicture(filename, self.file_path, thumbnail_path)
        yield self.resize_picture()

        self.finish()

    @gen.coroutine
    def resize_picture(self):
        image = Image.open(self.file_path)
        max_width = 840
        max_height = 560
        size = max_width, max_height

        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif=dict(image._getexif().items())

            if exif[orientation] == 3:
                image=image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image=image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image=image.rotate(90, expand=True)
        except Exception as exc:
            logging.info('pictures does not have exif for orientation')

        image.thumbnail(size)
        photo_thumb_path = os.path.join(self.thumbnails_path, self.filename)

        if image.mode in ('RGBA', 'LA'):
            image = image.convert("RGB")
        image.save(photo_thumb_path, "JPEG")
        return photo_thumb_path
