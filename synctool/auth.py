from base64 import b64decode

from django.http import HttpResponse
from django.utils import six


def decode_header(key):
    auth = (key or "").strip().replace("Basic ", "")
    try:
        credentials = decode(auth)
    except Exception:
        credentials = None, None

    if len(credentials) != 2:
        credentials = None, None

    return credentials


def decode(value):
    value = b64decode(value)
    if six.PY3:
        value = value.decode('utf-8')
    return value.split(":")


def require_token(token):
    def decorator(func):
        def inner(request, *args, **kwargs):
            key = request.META.get("HTTP_AUTHORIZATION")
            username, password = decode_header(key)

            authorized = (username or password) == token

            if not authorized:
                response = HttpResponse(
                    content="HTTP Authentication failed\n",
                    status=401,
                )
                response["WWW-Authenticate"] = 'Basic realm="Sync API"'
                return response

            return func(request, **kwargs)
        return inner
    return decorator
