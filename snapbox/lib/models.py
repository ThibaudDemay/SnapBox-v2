# @File: models.py
# @Author: Thibaud Demay (demay.thibaud@gmail.com)
# @Date:   30/03/2019 15:11:59
# @Last Modified by:   Thibaud Demay (demay.thibaud@gmail.com)
# @Last Modified time: 11/03/2020 06:28:25
# @License:
# The MIT License (MIT)
# Copyright (c) 2019-2020 Thibaud Demay
# Show license file in root folder.

from lib import database as db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class Picture(db.Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=func.now())
    name = Column(String)
    path = Column(String)
    thumbnail_path = Column(String)


class PictureSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Picture
