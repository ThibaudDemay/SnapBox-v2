import logging
import logging.handlers


class Color(object):

    RESET = "\033[0m"
    BOLD = "\033[1m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    GREY = "\033[37m"

    LightRED = "\033[91m"
    LightGREEN = "\033[92m"
    LightYELLOW = "\033[93m"
    LightBLUE = "\033[94m"
    LightPURPLE = "\033[95m"
    LightCYAN = "\033[96m"
    WHITE = "\033[97m"

    ORANGE = "\033[38;5;208m"


class AppLogFormatter(logging.Formatter):
    def __init__(self, *args, logging_pretty=False, **kwargs):
        super().__init__(*args, *kwargs)
        self.logging_pretty = logging_pretty

    def formatException(self, exc_info):
        if self.logging_pretty:
            return "%s%s%s" % (Color.ORANGE, super().formatException(exc_info), Color.RESET)

        else:
            return super().formatException(exc_info)

    def format(self, record):
        if self.logging_pretty:
            if record.levelno > 30:
                # log.error
                color = Color.LightRED

            elif record.levelno > 20:
                # log.warn
                color = Color.LightYELLOW

            elif record.levelno > 10:
                # log.info
                color = Color.LightGREEN

            elif record.levelno > 0:
                # log.debug
                color = Color.WHITE

            else:
                color = None

            if color is None:
                return super().format(record)

            return "%s%s%s" % (color, super().format(record), Color.RESET)

        else:
            return super().format(record)
