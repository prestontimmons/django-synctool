from django.conf import settings

from .functions import get_images, sync_data


class Client(object):

    def __init__(self, api_token=None, api_url=None, media_url=None):
        self.api_token = api_token or settings.SYNCTOOL_CLIENT_TOKEN
        self.api_url = api_url or settings.SYNCTOOL_CLIENT_ENDPOINT
        self.media_url = media_url

    def get_url(self, url):
        return "%s%s/" % (self.api_url, url)

    def sync(self, url, **kwargs):
        sync_data(
            url=self.get_url(url),
            api_token=self.api_token,
            clean=kwargs.get("clean", False),
            reset=kwargs.get("reset", True),
            images=kwargs.get("images", False),
            media_url=self.media_url,
        )

    def images(self, queryset, field):
        get_images(
            base_url=self.media_url,
            queryset=queryset,
            field=field,
        )
