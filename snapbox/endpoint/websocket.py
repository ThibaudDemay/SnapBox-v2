import logging

from snapbox.endpoint.base import WebSocketBaseHandler


class ServerWebSocketHandler(WebSocketBaseHandler):
    def __init__(self, *args, **kwargs):
        super(ServerWebSocketHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def open(self):
        logging.debug("WebSocket opened")
        self.application.add_websocket(self)

    def on_message(self, message):
        pass
        # self.write_message(u"You said: " + message)

    def on_close(self):
        self.application.remove_websocket(self)
        logging.debug("WebSocket closed")
