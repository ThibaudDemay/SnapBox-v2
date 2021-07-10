import json

import tornado.web
from tornado.web import HTTPError

from endpoint.base import BaseHandler
from snapbox.lib.models import Picture, PictureSchema

picture_schema = PictureSchema()
pictures_schema = PictureSchema(many=True)


class PicturesHandler(BaseHandler):
    def get(self):
        all_pictures = self.db.query(Picture).order_by(Picture.date.desc()).all()
        dump = pictures_schema.dump(all_pictures)
        self.write(json.dumps(dump))


class PictureHandler(BaseHandler):
    def get(self, id):
        picture = self.db.query(Picture).get(id)
        if picture:
            dump = picture_schema.dump(picture)
            self.write(json.dumps(dump))
        else:
            raise HTTPError(404, u"Picture not found")
