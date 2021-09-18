import exceptions
import jwt


def block_external_call(func):
    def wrapper(*args, **kwargs):
        handler = args[0]  # self
        if handler.request.remote_ip in ["127.0.0.1"]:
            return func(*args, **kwargs)
        else:
            raise exceptions.UnauthorizedError()

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
                raise exceptions.UnauthorizedError()
            return func(*args, **kwargs)
        else:
            raise exceptions.AuthError()

    return wrapper
