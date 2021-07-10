# @File: picture.py
# @Author: Thibaud Demay (demay.thibaud@gmail.com)
# @Date:   30/03/2019 15:11:59
# @Last Modified by:   Thibaud Demay (demay.thibaud@gmail.com)
# @Last Modified time: 11/03/2020 06:27:15
# @License:
# The MIT License (MIT)
# Copyright (c) 2019-2020 Thibaud Demay
# Show license file in root folder.

from lib.models import Picture


class PictureManager:
    def __init__(self, database_manager):
        self.__dbm = database_manager
        self.pics = list()

    def addPicture(self, name, path, thumbnail_path):
        p = Picture(name=name, path=path, thumbnail_path=thumbnail_path)
        self.pics.append(p)
        self.__dbm.add(p)

        return p
