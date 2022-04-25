import jwt

from snapbox.exceptions import AuthError, UnauthorizedError


def block_external_call(func):
    def wrapper(*args, **kwargs):
        handler = args[0]  # self
        debug = handler.application.settings.get("debug", False)
        if handler.request.remote_ip in ["127.0.0.1"] or debug:
            return func(*args, **kwargs)
        else:
            raise UnauthorizedError()

    return wrapper


def require_auth(func):
    def wrapper(*args, **kwargs):
        handler = args[0]
        auth = handler.request.headers.get("Authorization")
        if auth:
            try:
                parts = auth.split()
                token = parts[1]
                jwt.decode(
                    token, handler.admin_conf.JWT_SECRET, algorithms=handler.server_settings.get("JWT_ALGORITHM")
                )
            except Exception:
                raise UnauthorizedError()
            return func(*args, **kwargs)
        else:
            raise AuthError()

    return wrapper
