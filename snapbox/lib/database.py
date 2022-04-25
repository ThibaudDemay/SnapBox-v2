# @File: database.py
# @Author: Thibaud Demay (demay.thibaud@gmail.com)
# @Date:   30/03/2019 15:11:59
# @Last Modified by:   Thibaud Demay (demay.thibaud@gmail.com)
# @Last Modified time: 11/03/2020 06:28:56
# @License:
# The MIT License (MIT)
# Copyright (c) 2019-2020 Thibaud Demay
# Show license file in root folder.

import logging

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import SingletonThreadPool  # NullPool, QueuePool

from snapbox.lib.common import ConfigFile

Base = declarative_base()


class DatabaseManager:
    def __init__(self):
        self.dbSettings = ConfigFile().getSection("db")

        logging.debug("Init DB sqlite://%s" % self.dbSettings["path"])
        # self.engine = db.create_engine('sqlite:///%s' % self.dbSettings['path'], pool_size=20, max_overflow=0)
        self.engine = db.create_engine(
            "sqlite:///%s" % self.dbSettings["path"], isolation_level="SERIALIZABLE", poolclass=SingletonThreadPool
        )  # , pool_size=20
        self.engine.connect()
        self.session = db.orm.scoped_session(db.orm.sessionmaker(bind=self.engine))

        Base.metadata.create_all(self.engine)

    def add(self, object):
        self.session.add(object)
        self.session.commit()
