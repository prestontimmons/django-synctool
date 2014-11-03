Syncing data from a remote api
==============================

This library provides a client for syncing data from a remote url.

Begin by creating a client instance:

.. code-block:: python

    from synctools.client import Client

    client = Client(
        api_url="https://<remote-server.com>/sync/",
        api_token="<mytoken>",
    )

Now, you can try syncing data from a remote api:

.. code-block:: python

    client.sync("<path>")


Cleaning local data
-------------------

It's often preferable to delete local data before saving the remote
information. The ``sync`` function will do this if you passing the
``clean`` argument.

.. code-block:: python

    client.sync("<path>", clean=True)

This step is especially helpful if you’ve made local edits to your database.
If you’ve made local changes that conflict with the remote queryset, and do
not clear your local data, the sync process can fail with an
``IntegrityError``.


Downloading images
------------------

The ``sync`` command can be instructed to download remote images in addition
to saving the database information. To do this, pass ``images`` argument.

.. code-block:: python

    client.sync("<path>", images=True)

When syncing images, make sure to also pass a ``media_url`` argument to the
``Client`` class. Images synced this way will be downloaded for every
``ImageField`` of every model type in the data returned by the remote url.
If images already exist locally, the download will be skipped.


Reset sequence
--------------

After completing a sync, the ``sync_data`` command resets the primary key
sequence for each application the remote querysets belonged to. Without
this step, adding new items to your local database may fail with integrity
errors.

If you do not want to reset the sequence for some reason, pass ``reset``
as ``False``.

.. code-block:: python

    client.sync("<path>", reset=False)


Downloading images manually
---------------------------

You can manually initiate the download image process. This is helpful if:

* You already have local data that you want to download images for
* You only want to download images for certain fields of a model

.. code-block:: python

    client = Client(
        media_url="http://<remote-server.com>/<mediaroot>/",
    )

    client.images(
        queryset=Post.objects.all(),
        field="hero_image"
    )

This will download and save an image for each entry in the queryset. If
the image entry is empty, or the local image already exists, the download
is skipped.

.. note::

    This function assumes you're using file storage in your local
    environment.
