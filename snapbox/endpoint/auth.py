import hashlib
import json
from datetime import datetime, timedelta

import jwt
from tornado import gen

from snapbox.endpoint.base import BaseHandler
from snapbox.exceptions import AuthUserNotFoundError, AuthWrongCredentialsError


class AuthLoginHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        data = json.loads(self.request.body)
        username = data.get("username", "")
        password = data.get("password", "")
        password_encrypted = hashlib.sha512(password.encode("utf-8")).hexdigest()

        if username and username == self.admin_conf.username:
            if password and password_encrypted == self.admin_conf.password:
                payload = {
                    "admin": True,
                    "exp": datetime.utcnow() + timedelta(seconds=self.server_settings.get("JWT_EXP_DELTA_SECONDS")),
                }
                jwt_token = jwt.encode(
                    payload, self.admin_conf.JWT_SECRET, algorithm=self.server_settings.get("JWT_ALGORITHM")
                )
                response = {"token": jwt_token}
                self.write(response)
            else:
                raise AuthWrongCredentialsError()
        else:
            raise AuthUserNotFoundError()
