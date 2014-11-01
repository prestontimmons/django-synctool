try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.conf import settings
from django.conf.urls import url
from django.core.management.commands.dumpdata import Command
from django.core.serializers import serialize
from django.http import HttpResponse

from .auth import require_token


class Route(object):

    def __init__(self, *args, **kwargs):
        self.api_token = (
            kwargs.get("api_token") or settings.SYNCTOOL_API_TOKEN
        )
        self.urlpatterns = []

    def queryset(self, path):
        def decorator(func):
            def inner(request, **kwargs):
                querysets = func(**kwargs)
                data = self.serialize(querysets)

                return HttpResponse(
                    content=data,
                    content_type="application/json",
                )

            self.add_url(path, inner)

            return inner
        return decorator

    def app(self, path, label):
        def view(request):
            cmd = Command()
            cmd.stdout = StringIO()
            cmd.handle(label, format="json", exclude=[])
            return HttpResponse(
                content=cmd.stdout.getvalue(),
                content_type="application/json",
            )

        self.add_url(path, view)

        return view

    def add_url(self, path, func):
        auth = require_token(token=self.api_token)
        self.urlpatterns.append(
            url(
                regex="^%s/?$" % path,
                view=auth(func),
            ),
        )

    def serialize(self, querysets):
        return serialize_querysets(querysets)


def serialize_querysets(querysets):
    if not type(querysets) in (list, tuple):
        querysets = [querysets]

    def get_objects():
        for queryset in querysets:
            for obj in queryset:
                yield obj

    return serialize("json", get_objects())
