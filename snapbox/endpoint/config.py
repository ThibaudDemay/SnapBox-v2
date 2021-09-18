import json
import os
import shutil

from decorators import require_auth
from endpoint.base import BaseHandler
from tornado import gen


class ConfigHandler(BaseHandler):
    """
    Info :
        - Storage Path
        - Storage Usage
        - Picture Count (PhotoBooth et ext ?)
        - Camera Connect ?
        - Camera Model
    Config :
        - Countdown Preview
        - Countdown Sec
        - Reset Factory
    """

    @gen.coroutine
    def prepare(self):
        yield super().prepare()

        # storage usage
        self.sto_total, self.sto_used, self.sto_free = shutil.disk_usage(self.app_conf.save_path)
        self.pics_count = sum(len(files) for _, _, files in os.walk(self.pictures_path))
        self.exts_count = sum(len(files) for _, _, files in os.walk(self.external_path))

    @gen.coroutine
    def get(self):
        self.write(self.get_config())

    @gen.coroutine
    @require_auth
    def put(self):
        data = json.loads(self.request.body)
        countdown_min = self.server_settings.get("countdown_min")
        countdown_max = self.server_settings.get("countdown_max")
        countdown = data.get("countdown")
        preview = data.get("preview")
        changed = False

        if "countdown" in data.keys() and countdown_min <= countdown and countdown_max >= countdown:
            self.app_conf.countdown = countdown
            changed = True
        if "preview" in data.keys():
            self.app_conf.preview = preview
            changed = True

        if changed:
            self.application.save_config()
        self.write(self.get_config())

    def get_config(self):
        return json.dumps(
            {
                "path": {
                    "sto_path": self.app_conf.save_path,
                    "pics_path": self.pictures_path,
                    "thumb_path": self.thumbnails_path,
                    "ext_path": self.external_path,
                },
                "sto_usage": {"total": self.sto_total, "used": self.sto_used, "free": self.sto_free},
                "pics_count": self.pics_count,
                "exts_count": self.exts_count,
                "camera_state": self.camera.get_connect(),
                "camera_model": self.camera.get_model(),
                "countdown": self.app_conf.countdown,
                "preview": self.app_conf.preview,
            }
        )
