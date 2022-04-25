import mimetypes

from tornado.web import HTTPError

from snapbox.endpoint.base import BaseHandler
from snapbox.lib.models import Picture


class AssetsHandler(BaseHandler):
    def get(self, id):
        picture = self.db.query(Picture).get(id)
        if picture:
            try:
                mimetype = mimetypes.MimeTypes().guess_type(picture.thumbnail_path)[0]
                self.set_header("Content-Type", mimetype)
                with open(picture.thumbnail_path, "rb") as f:
                    data = f.read()
                    self.write(data)
                self.finish()
            except Exception as exc:
                print(exc)
        else:
            raise HTTPError(404, "Picture not found")
