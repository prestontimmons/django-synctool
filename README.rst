Django Synctool
===============

Synctool is a library for Django to make syncing querysets between
databases easy. No more manually dumping or entering data. No more
out-of-date fixtures. Just get the data you want, on demand.


Basic usage
-----------

Here's an example for syncing the ``django.contrib.sites`` app.

**1. Create an api view**

.. code-block:: python

    # myapp.views

    from synctools.routing import Route

    route = Route()

    @route.app("sites", "sites")


**2. Add the urls to your project**

.. code-block:: python

    # myproject.urls

    from django.conf.urls import include, url
    from myapp.views import route

    urlpatterns += [
        url("^sync/", include(route.urlpatterns)),
    ]


**3. Sync data from the remote endpoint**

.. code-block:: python

    # myclient.py

    from synctools.client import Client

    client = Client(
        api_url="https://myserver.com/sync/",
        api_token="<token>",
    )

    if __name__ == "__main__":
        client.sync("sites")

The sites app can now be synced locally from a remote data source by
calling:

::

    python myclient.py


How it works
~~~~~~~~~~~~

Under the hood Synctool uses the Django JSON serializer to pass data
between servers. Synctool isn't limited to syncing whole applications.
It can also sync custom querysets and even download associated images.


Installation
------------

Synctool can be installed from PyPI:

::
    
    pip install django-synctool


Requirements
------------

This library requires Django >= 1.7 and either Python 2.7 or Python >= 3.3.
