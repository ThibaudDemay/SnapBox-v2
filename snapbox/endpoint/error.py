"""
ErrorHandler
"""

from tornado.web import ErrorHandler

import exception as exception
from endpoint.base import BaseHandler


class ErrorBadUriHandler(ErrorHandler, BaseHandler):
    """Error Handler return by default Bad URI"""

    def prepare(self):
        raise exception.BadURI()
