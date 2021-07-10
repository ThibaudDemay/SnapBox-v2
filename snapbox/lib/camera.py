# @File: camera.py
# @Author: Thibaud Demay (demay.thibaud@gmail.com)
# @Date:   09/04/2019 15:52:27
# @Last Modified by:   Thibaud Demay (demay.thibaud@gmail.com)
# @Last Modified time: 11/03/2020 06:29:36
# @License:
# The MIT License (MIT)
# Copyright (c) 2019-2020 Thibaud Demay
# Show license file in root folder.

import logging
import os
import time

import gphoto2 as gp


class Camera:
    def __init__(self, pictures_path, thumbnails_path, picture_manager):
        self._camera = None
        self._hasCamInited = False

        self.pictures_path = pictures_path
        self.thumbnails_path = thumbnails_path
        self.pm = picture_manager

        self.load()

    def load(self):
        ret = False

        ret &= self.connect()
        ret &= self.load_config()

        return ret

    def connect(self):
        try:
            self._camera = gp.Camera()
            self._camera.init()
            self._hasCamInited = True
        except Exception as exc:
            self._hasCamInited = False
            logging.error("No Camera : %s" % str(exc))
            return False
        else:
            return True

    def load_config(self):
        if self._hasCamInited:
            try:
                self._camera_config = self._camera.get_config()
            except Exception as exc:
                self._hasCamInited = False
                logging.error("No Camera : %s" % str(exc))
                return False
            else:
                return True
        return False

    def get_connect(self):
        self.load_config()
        return self._hasCamInited

    def get_model(self):
        camera_model = "N/A"

        self.load_config()

        if self._hasCamInited:
            OK, camera_model = gp.gp_widget_get_child_by_name(self._camera_config, "cameramodel")
            if OK < gp.GP_OK:
                OK, camera_model = gp.gp_widget_get_child_by_name(self._camera_config, "model")
            if OK >= gp.GP_OK:
                camera_model = camera_model.get_value()

        return camera_model

    def start_preview_mode(self):
        self.load_config()
        if not self._hasCamInited and not self.load():
            return False

        gp.gp_camera_capture_preview(self._camera)

    def stop_preview_mode(self):
        self.load_config()
        if not self._hasCamInited and not self.load():
            return False

        OK, viewfinder = gp.gp_widget_get_child_by_name(self._camera_config, "viewfinder")
        if OK >= gp.GP_OK:
            viewfinder.set_value(0)
            self._camera.set_config(self._camera_config)

    def do_preview(self):
        if not self._hasCamInited:
            return False
        OK, preview = gp.gp_camera_capture_preview(self._camera)
        if OK < gp.GP_OK:
            return False
        logging.debug("preview file %s", preview)
        return preview

    def capture_image(self):
        self.load_config()
        if not self._hasCamInited and not self.load():
            return None

        ct_cfg = self._camera_config.get_child_by_name("capturetarget")
        ct = ct_cfg.get_value()
        ct_cfg.set_value("Internal RAM")
        self._camera.set_config(self._camera_config)

        # do capture
        path = self._camera.capture(gp.GP_CAPTURE_IMAGE)
        logging.debug("Capture cam path: %s %s" % (path.folder, path.name))
        cam_file = self._camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)

        # save image
        ts = int(time.time())
        name = "%s.jpg" % str(ts)
        pics_path = os.path.join(self.pictures_path, name)
        logging.debug("Path of pics : %s" % pics_path)
        cam_file.save(pics_path)
        self._camera.file_delete(path.folder, path.name)

        thumb_path = os.path.join(self.thumbnails_path, name)
        picture = self.pm.addPicture(name, pics_path, thumb_path)

        # reset conf
        ct_cfg.set_value(ct)
        self._camera.set_config(self._camera_config)

        return picture
