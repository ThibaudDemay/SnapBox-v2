import asyncio
import hashlib
import json
import logging
import os
import secrets
import sys

from docopt import docopt
from endpoint.assets import AssetsHandler
from endpoint.auth import AuthLoginHandler
from endpoint.config import ConfigHandler
from endpoint.error import ErrorBadUriHandler
from endpoint.pictures import PictureHandler, PicturesHandler
from endpoint.snap import SnapHandler
from endpoint.websocket import ServerWebSocketHandler
from lib.camera import Camera
from lib.common import ConfigFile, json2obj
from lib.database import DatabaseManager
from lib.picture import PictureManager
from log import AppLogFormatter
from pyudev import Context, Monitor, MonitorObserver
from tornado import httpserver, ioloop
from tornado.log import access_log
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.web import Application, RequestHandler


class SnapBoxServer(Application):
    def __init__(self, args):
        handlers = [
            (r"^/config/?", ConfigHandler),
            (r"^/pictures/?", PicturesHandler),
            (r"^/pictures/(\d+)?", PictureHandler),
            (r"^/assets/(\d+)", AssetsHandler),  # RENVOIE THUMBNAIL (NEED REWORK ?)
            (r"^/upload/(?P<filename>.*)", None),  # /upload/<filename>
            (r"^/ws/server?", ServerWebSocketHandler),  # SINON PASSAGE SUR WS POUR LE SNAP
            # only on localhost/127.0.0.1
            (r"^/snap/?", SnapHandler),  # QUID DU DELAI
            # AUTH
            (r"^/auth/login/?", AuthLoginHandler),
        ]
        settings = dict(
            autoreload=args["--autoreload"],
            debug=args["--debug"],
            default_handler_class=ErrorBadUriHandler,
            default_handler_args=dict(status_code=404),
            websocket_ping_interval=60,
        )
        Application.__init__(self, handlers, **settings)
        self.server_settings = ConfigFile().getSection("server")
        self.load_config()
        self.dbm = DatabaseManager()
        self.pm = PictureManager(self.dbm)
        self.camera = Camera(self.pictures_path, self.thumbnails_path, self.pm)
        self.event_handler = None
        self.websockets = list()

        self.udev_init()

    def load_config(self):
        self.pictures_folder = self.server_settings["pictures_folder"]
        self.thumbnails_folder = self.server_settings["thumbnails_folder"]
        self.external_folder = self.server_settings["external_folder"]
        self.server_conf = ConfigFile(self.server_settings["server_conf"]).read()
        self.app_conf = json2obj(self.server_conf["app"])
        self.http_conf = json2obj(self.server_conf["http"])
        self.admin_conf = json2obj(self.server_conf["admin"])

        self.pictures_path = os.path.join(self.app_conf.save_path, self.pictures_folder)
        if not os.path.exists(self.pictures_path):
            os.makedirs(self.pictures_path, exist_ok=True)
        self.thumbnails_path = os.path.join(self.app_conf.save_path, self.thumbnails_folder)
        if not os.path.exists(self.thumbnails_path):
            os.makedirs(self.thumbnails_path, exist_ok=True)
        self.external_path = os.path.join(self.app_conf.save_path, self.external_folder)
        if not os.path.exists(self.external_path):
            os.makedirs(self.external_path, exist_ok=True)

    def udev_init(self):
        context = Context()
        # Monitoring USB Connection
        monitor_usb = Monitor.from_netlink(context)
        monitor_usb.filter_by(subsystem="usb")
        self.observer_usb = MonitorObserver(monitor_usb, callback=self.usb_device_event, name="usb-monitor-observer")
        self.observer_usb.start()

    def usb_device_event(self, device):
        if device.action in ["add", "remove"] and device.device_type == "usb_interface":
            logging.info("background event {device.action}: {device.device_path}".format(device=device))
            self.camera.load()
            self.send_msg_to_websockets(
                {
                    "event": "update",
                    "type": "state",
                    "mutation": "camera/setIsConnected",
                    "value": self.camera.get_connect(),
                }
            )

    def add_websocket(self, websocket):
        if websocket not in self.websockets:
            self.websockets.append(websocket)
            self.send_init_event_to_websocket(websocket)

    def remove_websocket(self, websocket):
        if websocket in self.websockets:
            self.websockets.remove(websocket)

    def send_init_event_to_websocket(self, websocket):
        events = [
            {
                "event": "update",
                "type": "state",
                "mutation": "camera/setIsConnected",
                "value": self.camera.get_connect(),
            }
        ]
        for event in events:
            websocket.write_message(json.dumps(event))

    def send_msg_to_websockets(self, msg_json):
        for websocket in self.websockets:
            websocket.write_message(json.dumps(msg_json))

    def log_request(self, handler: RequestHandler) -> None:
        """Writes a completed HTTP request to the logs."""
        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return

        if handler.get_status() < 400:
            log_method = access_log.info

        elif handler.get_status() < 500:
            log_method = access_log.warning

        else:
            log_method = access_log.error

        request_time = 1000.0 * handler.request.request_time()

        if handler.exc_name:
            log_method(
                "%d %s %.2fms - %s ", handler.get_status(), handler._request_summary(), request_time, handler.exc_name
            )
        elif handler.action_name:
            log_method(
                "%d %s %.2fms - %s", handler.get_status(), handler._request_summary(), request_time, handler.action_name
            )
        else:
            log_method("%d %s %.2fms - Ok", handler.get_status(), handler._request_summary(), request_time)


def generate_tokens(conf):
    server_conf_file = ConfigFile(conf["server_conf"])
    server_conf = server_conf_file.read()
    server_conf["admin"]["JWT_SECRET"] = secrets.token_urlsafe(32)
    server_conf_file.write(server_conf)


def update_admin_password(conf):
    server_conf_file = ConfigFile(conf["server_conf"])
    server_conf = server_conf_file.read()
    password = input("New password for admin user : ")
    server_conf["admin"]["password"] = hashlib.sha512(password.encode("utf-8")).hexdigest()
    server_conf_file.write(server_conf)


def parse_args(args, conf):

    if args["--generate-tokens"]:
        generate_tokens(conf)
        exit(0)

    if args["--password-admin"]:
        update_admin_password(conf)
        exit(0)

    root = logging.getLogger()
    if args["--stdout"]:
        AppLogHandler = logging.StreamHandler(sys.stdout)
    else:
        log_path = conf.get("log_path", "server.log") if conf else "server.log"
        AppLogHandler = logging.FileHandler(log_path, "a+")

    if args["--debug"]:
        AppLogHandler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
    else:
        AppLogHandler.setLevel(logging.INFO)
        root.setLevel(logging.INFO)

    AppLogHandler.setFormatter(
        AppLogFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", logging_pretty=True)
    )
    root.addHandler(AppLogHandler)

    logging.debug(args)


def main():
    """Snapbox Server

    Usage:
        snapbox-server [options]
        snapbox-server -g | --generate-tokens
        snapbox-server -p | --password-admin
        snapbox-server -h | --help
        snapbox-server --version

    Options:
        -d --debug              Activate debug logging.
        -s --stdout             Activate out on stdout.
        -a --autoreload         Activate auto reload.
        -h --help               Show this screen.
        -g --generate-tokens    Generate tokens secret of app.
        -p --password-admin     Change admin password.
        --version               Show version.
    """
    conf = ConfigFile().getSection("server")
    args = docopt(main.__doc__)
    parse_args(args, conf)
    logging.info("Starting SnapBox Api Server")

    # Needed for watchdog on FileSytem watching files changes
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    app = SnapBoxServer(args)  # Replace by custom app
    http_server = httpserver.HTTPServer(app)
    http_server.listen(app.http_conf.port)
    logging.info("Listening on http://%s:%s" % (app.http_conf.addr, app.http_conf.port))
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
