"""
ErrorHandler
"""

from tornado.web import ErrorHandler

from snapbox.endpoint.base import BaseHandler
from snapbox.exceptions import BadURI


class ErrorBadUriHandler(ErrorHandler, BaseHandler):
    """Error Handler return by default Bad URI"""

    def prepare(self):
        raise BadURI()
