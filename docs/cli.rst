Creating a command-line interface
=================================

If you sync more than a few models, it's nice to wrap that up in a
command-line interface. This can be done easily using the `Click`_
library.


Example interface
-----------------

.. code-block:: python

    # sync.py

    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"

    import django
    django.setup()

    import click
    from synctool.client import Client


    client = Client(
        api_url="<remote-url>",
        media_url="<media-url>",
    )


    @click.group()
    def cli():
        """A tool for syncing data."""


    @cli.command()
    @click.option("--clean/--no-clean", default=False)
    @click.option("--images/--no-images", default=False)
    def blogs(clean, images):
        """ Sync blogs """
        client.sync("blogs", clean=True)


    if __name__ == "__main__":
        cli()


Now you can sync data using a command like:

::

    python sync.py blogs --clean


You can make this yet better by `integrating with setuptools`_.

This would enable you to simplify it to something like:

::

    sync blogs --clean

Further, if your application is installed in a virtualenv, you can call
the command without needing to activate the virtualenv.


.. _Click: http://click.pocoo.org/

.. _integrating with setuptools: http://click.pocoo.org/3/setuptools/
