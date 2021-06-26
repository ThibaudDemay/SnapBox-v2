import logging

from snapbox.endpoint.base import BaseHandler


class SnapHandler(BaseHandler):
    def get(self):
        pics_path = self.camera.capture_image()
        logging.debug("do_capture")

        self.write({"pics_path": pics_path})
