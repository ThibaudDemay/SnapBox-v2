class BaseException(Exception):
    """BaseException for api exception"""

    status = 500
    message = "We encountered an internal error. Please try again."
    resource = ""
    request_id = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return str(self.message)

    def get_status(self):
        """Get HTTP code status"""
        return self.status

    def get_message(self):
        """Get message defined in exception"""
        return self.message


class BadURI(BaseException):
    """Bad URI was Reached by user on API"""

    status = 404
    message = "Bad URI."


class InternalError(BaseException):
    """Internal error, not defined error please check log"""

    status = 500
    message = "We encountered an internal error. Please try again."


class NotImplemented(BaseException):
    """Not Implemented error use when handler method blank"""

    status = 501
    message = "Not implemented."
