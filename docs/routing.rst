Adding api views
================

In order to sync data, a remote server must make it available for download.
This can be achieved using the ``synctool.routing.Route`` class. This class
takes care of:

* Creating the url pattern
* Serializing the returned data using the Django JSON serializer
* Returning an ``application/json`` response object
* Adding http basic authentication to the api


Serializing an application
--------------------------

The ``route.app`` function can be used to serialize a whole application.
The returned data is the same as that of the ``python manage.py dumpdata``
command.

.. py:function:: route.app(path, label)

    :param path: The path of the urlpattern to register.
    :param label: The label of the installed application to serialize.

Example:

.. code-block:: python

    from synctools.routing import Route

    route = Route()

    # Sync the ``django.contrib.sites`` app
    route.app("sites", "sites")

    # Sync an application call myblogapp
    route.app("blogs", "myblogapp")


Once your urlpatterns are registered, you can open the url in a browser
to inspect the data.


Serializing querysets
---------------------

The ``route.queryset`` decorator can be used to register any function
that returns one or more querysets.

.. py:function:: route.queryset(path)

    :param path: The path of the urlpattern to register.


Returning a single queryset
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code-block:: python

    from myapp.models import Blog

    @route.queryset("blogs")
    def blogs():
        return Blog.objects.all()


Returning multiple querysets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multiple querysets can be returned as a list or tuple:

.. code-block:: python

    from myapp.models import Blog, Post

    @route.queryset("blogs")
    def blogs():
        return [
            Blog.objects.all(),
            Post.objects.all(),
        ]


Filtering and slicing
~~~~~~~~~~~~~~~~~~~~~

Querysets can be filtered or sliced. This is useful when you only want
to return a subset of a table.

Example:

.. code-block:: python

    @route.queryset("blogs")
    def blogs():
        return [
            Blog.objects.all()[:100],
        ]


Accepting arguments
~~~~~~~~~~~~~~~~~~~

The route argument is a url regular expression. This means views can take
arguments from the url.

Example:

.. code-block:: python

    @route.queryset("blog/(?P<slug>[^/]+)")
    def blog(slug):
        return Blog.objects.filter(slug=slug)


Modifying querysets
~~~~~~~~~~~~~~~~~~~

Querysets can be modified before returning them. This can be helpful if
you want to exclude certain information in the output.

For example, if ``Blog`` had a ``User`` relation, we could return a ``Blog``
queryset but leave out the user information.

Example:

.. code-block:: python

    @route.queryset("blogs")
    def pickle_blog():
        queryset = Blog.objects.all()
        for blog in queryset:
            blog.user = None
        return queryset

Note: This example assumes the user field is nullable.


Order is important
~~~~~~~~~~~~~~~~~~

When syncing applications using the ``route.app`` function, model
dependencies are automatically calculated and sorted. When using
``route.queryset``, this is not the case. Therefore, you must pay
attention to the order in which you return querysets.

For example, assume you had a ``Blog`` and ``Post`` model. The ``Post``
model has a foreign key to ``Blog``:

.. code-block:: python

    @route.queryset("blogs")
    def blogs():
        # Good: Post depends on blog existing first. Since blog
        # is serialized first, blog will be saved first.
        return [
            Blog.objects.all(),
            Post.objects.all(),
        ]

    @route.queryset("blogs")
    def blogs():
        # Bad: The sync client can fail with an IntegrityError because
        # post points to blogs that haven't been saved locally yet.
        return [
            Post.objects.all(),
            Blog.objects.all(),
        ]


.. _api-authentication:

Authentication
--------------

HTTP basic authentication is added to each view created using the ``Route``
class. By default, the credential is set to ``settings.SYNCTOOL_API_TOKEN``.
A custom token can be specified as an argument to the ``Route`` class.

Example:

.. code-block:: python

    route = Route(api_token="mytoken")

A sample call that grants access to this view would be:

.. code-block:: bash

    $ curl https://myserver.com/sync/sites -u mytoken:


.. note::

    If you want your queryset information and credentials to remain private,
    make sure to serve your API over SSL only.


Including urls
--------------

The routed url patterns can be included in your project in the same way
as other url patterns:

Example:

.. code-block:: python

    # myproject.urls

    from myapp.views import route

    urlpatterns += patterns("",
        url("^sync/", include(route.urlpatterns)),
    )
