"""
ErrorHandler
"""

import exceptions
from endpoint.base import BaseHandler
from tornado.web import ErrorHandler


class ErrorBadUriHandler(ErrorHandler, BaseHandler):
    """Error Handler return by default Bad URI"""

    def prepare(self):
        raise exceptions.BadURI()
