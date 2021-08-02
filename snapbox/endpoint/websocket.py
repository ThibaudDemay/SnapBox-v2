import logging

from endpoint.base import WebSocketBaseHandler


class ServerWebSocketHandler(WebSocketBaseHandler):

    def __init__(self, *args, **kwargs):
        super(ServerWebSocketHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def open(self):
        logging.debug("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        logging.debug("WebSocket closed")