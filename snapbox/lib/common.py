import fcntl
import json
import logging
import os
import sys

from lib import default_settings_cfgfile

class ConfigFile(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern, use the same instance ever"""

        if cls.instance is None:
            cls.instance = object.__new__(cls)
            cls.instance.locks = dict()

        return cls.instance

    def __init__(self, configfilePath=default_settings_cfgfile, decoder=None):
        self.configfile = configfilePath
        self.decoder = decoder

    def read(self):
        try:
            with open(self.configfile, "r") as cfg:
                config = cfg.read()

            if self.decoder is not None:
                return json.loads(config, cls=self.decoder)
            else:
                data = json.loads(config)
                return data

        except Exception as exc:
            logging.error("Cannot read config file %s : %s" % (self.configfile, exc))
            raise exc.with_traceback(sys.exc_info()[2])

    def write(self, config):
        try:
            if not isinstance(config, str):
                config = json.dumps(config, indent=4, sort_keys=True)

            with open(self.configfile, "w") as cfg:
                cfg.write(config)

            return True

        except Exception as exc:
            logging.error("Cannot write config file %s : %s" % (self.configfile, exc))
            raise exc.with_traceback(sys.exc_info()[2])

    def getSection(self, key, default=None):
        output = None
        settings = self.read()
        if key in settings:
            output = settings.get(key, default)
        return output

    def lock(self, lockName):
        """Lock a file with the name lockName (a lock file is created if missing).
        Location of the lock file is configured from the
        settings conf file (section:system, key:lock_file_path)"""

        lockPath = self.getSection("system")["lock_file_path"]
        try:
            lockFile = os.path.join(lockPath, lockName)
            if lockName not in self.locks.keys():
                fd = open(lockFile, "w")
                self.locks[lockName] = fd
            else:
                fd = self.locks[lockName]
            fcntl.flock(fd, fcntl.LOCK_EX)
        except Exception as e:
            logging.error("Error while locking [%s] : %s" % (lockName, e))

    def unlock(self, lockName):
        """Unlock the file previously locked."""
        try:
            if lockName in self.locks:
                fd = self.locks[lockName]
                fcntl.flock(fd, fcntl.LOCK_UN)
                fd.close()
                self.locks.pop(lockName)
            else:
                logging.debug("No lock saved with name %s" % lockName)
        except Exception as e:
            logging.error("Error while unlocking %s : %s" % (lockName, e))

    def hasLock(self, lockName):
        """Check if existing lock exists on the ressource"""
        lockPath = self.getSection("system")["lock_file_path"]
        lockFile = os.path.join(lockPath, lockName)
        return os.path.exists(lockFile)


def json2obj(data):
    return type("new_dict", (object,), data)
