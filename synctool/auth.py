from base64 import b64decode

from django.http import HttpResponse


def decode_header(key):
    auth = (key or "").strip().replace("Basic ", "")
    try:
        credentials = b64decode(auth).split(":")
    except:
        credentials = None, None

    if len(credentials) != 2:
        credentials = None, None

    return credentials


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
