API reference
=============

This provides a reference to the public classes and functions.


.. module:: synctools.client
    :synopsis: The sync client class.


The Client class
----------------

.. class:: Client

    The ``Client`` class provides functions for downloading remote
    data and images.

Methods
~~~~~~~

.. method:: Client.__init__(api_token=None, api_url=None, media_url=None)

    Instantiates a ``Client`` object.

    ``api_token`` is the username used for HTTP basic authentication with
    the remote api. If this value isn't provided, it defaults to
    ``settings.SYNCTOOL_CLIENT_TOKEN``.

    ``api_url`` is the base url of the remote api to connect with. This
    would be something like ``https://myserver.com/sync/``. This value is
    prefixed to the url provided to the ``Client.sync`` function. If this
    value isn't provided, it defaults to
    ``settings.SYNCTOOL_CLIENT_ENDPOINT``.

    ``media_url`` is the base url from where remote media files are served.
    This is used if the client is instructed to download images.

.. method:: Client.sync(url, clean=False, reset=True, images=False)

    Syncs data from a remote api.

    ``url`` is the remote url to connect to. This is only the part of
    the url after ``self.api_url``. For example, if the api url is
    ``https://<remote-server>/sync/``, ``client.sync("sites")`` would
    connect to ``https://<remote-server>/sync/sites``.

    ``clean`` tells the client whether to delete local information before
    saving the remote data.

    ``reset`` tells the client whether reset the primary key sequence of
    the application tables after the sync is finished.

    ``images`` tells the client whether to download images for any image
    fields contained in the synced data.

.. method:: Client.images(queryset, field)

    Download remote images for a queryset. Images will be downloaded from
    the ``media_url`` client option.

    ``queryset`` is the queryset to download images for, i.e.
    ``Blog.objects.all()``

    ``field`` is the name of the image field to download images for.


.. module:: synctools.routing
    :synopsis: The sync route class.


The Route class
---------------

.. class:: Route

    The ``Route`` class creates views and urls for sync apis.

Methods
~~~~~~~

.. method:: Route.__init__(api_token=None)

    Instantiates a ``Route`` object.

    ``api_token`` is the authentication token to require for any clients
    connecting to this api. If this value isn't provided, it defaults
    to ``settings.SYNCTOOL_API_TOKEN``.

.. method:: Route.app(path, label)

    Creates a view to serialize data from a given app label.

    Example:

    .. code-block:: python

        route.app("blogs", "myblogapp")

    ``path`` is the url regex to serve the view from.

    ``label`` is the installed application label to serialize.

.. method:: Route.queryset(path)

    A decorator factory for views that serialize a given queryset.

    Example:

    .. code-block:: python

        @route.queryset("blogs")
        def blogs():
            return Blog.objects.all()

    ``path`` is the url regex to serve the view from.
