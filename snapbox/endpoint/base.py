"""
BaseHandler
"""

from tornado import gen
from tornado.log import app_log
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

import snapbox.exception as exception


class BaseHandler(RequestHandler):
    """
    Tornado Handler base of my other handler with integrate logging
    """

    # Used to dislay exception name in logs
    exc_name = None

    # Used to display Auth API Action name in logs
    action_name = None

    @property
    def db(self):
        return self.application.dbm.session

    @property
    def pm(self):
        return self.application.pm

    @property
    def camera(self):
        return self.application.camera

    @property
    def save_path(self):
        return self.application.save_path

    @property
    def pictures_path(self):
        return self.application.pictures_path

    @property
    def external_path(self):
        return self.application.external_path

    @property
    def thumbnails_path(self):
        return self.application.thumbnails_path

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, x-filename")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    @gen.coroutine
    def prepare(self):
        pass

    def log_exception(self, typ, value, tb):
        """Customize logging of uncaught exceptions.
        By default logs instances of `HTTPError` as warnings without
        stack traces (on the ``tornado.general`` logger), and all
        other exceptions as errors with stack traces (on the
        ``tornado.application`` logger).
        .. versionadded:: 3.1
        """
        if isinstance(value, exception.BaseException):
            self.exc_name = value.__class__.__name__

        else:
            app_log.error("%s - %s\n", self._request_summary(), value.__class__.__name__, exc_info=(typ, value, tb))

    def write_error(self, status_code, **kwargs):
        """Generate a S3 XML error response from an exception.
        All known exceptions are instance of BaseException.
        If an unknown exception is raised, we return an InternalError.
        """
        _, exc, _ = kwargs["exc_info"]

        if not isinstance(exc, exception.BaseException):
            exc = exception.BaseException()

        self.set_status(exc.get_status())
        self.write(exc.get_message())
        self.finish()


class WebSocketBaseHandler(WebSocketHandler):
    """
    Tornado Handler base of my other handler with integrate logging
    """

    # Used to dislay exception name in logs
    exc_name = None

    # Used to display Auth API Action name in logs
    action_name = None

    @property
    def event_handler(self):
        return self.application.event_handler

    @event_handler.setter
    def event_handler(self, event_handler):
        self.application.event_handler = event_handler

    @gen.coroutine
    def prepare(self):
        pass

    def log_exception(self, typ, value, tb):
        """Customize logging of uncaught exceptions.
        By default logs instances of `HTTPError` as warnings without
        stack traces (on the ``tornado.general`` logger), and all
        other exceptions as errors with stack traces (on the
        ``tornado.application`` logger).
        .. versionadded:: 3.1
        """
        if isinstance(value, exception.BaseException):
            self.exc_name = value.__class__.__name__

        else:
            app_log.error("%s - %s\n", self._request_summary(), value.__class__.__name__, exc_info=(typ, value, tb))

    def write_error(self, status_code, **kwargs):
        """Generate a S3 XML error response from an exception.
        All known exceptions are instance of BaseException.
        If an unknown exception is raised, we return an InternalError.
        """
        _, exc, _ = kwargs["exc_info"]

        if not isinstance(exc, exception.BaseException):
            exc = exception.BaseException()

        self.set_status(exc.get_status())
        self.write(exc.get_message())
        self.finish()
