from errno import EEXIST
import os
from os.path import isdir

import requests

from django.apps import apps
from django.core.serializers import deserialize
from django.core.management.color import no_style
from django.db import connection
from django.db.models import ImageField


def puts(value):
    try:
        verbosity = int(os.environ.get("SYNCTOOL_VERBOSITY", 1))
    except ValueError:
        verbosity = 1

    if verbosity > 0:
        print(value)


def sync_data(url, api_token, clean=False, reset=True, images=False,
        media_url=None):

    puts("Loading data from {0}".format(url))
    response = requests.get(url, auth=(api_token, ""))
    if not response.ok:
        puts(response.content)

        raise RuntimeError(
            "%s server error while contacting api." % response.status_code
        )

    app_labels = set()
    model_labels = set()
    models = []

    puts("Saving data")

    for obj in deserialize("json", response.content):
        app_labels.add(obj.object._meta.app_label)

        label = "%s.%s" % (
            obj.object._meta.app_label, obj.object._meta.model_name,
        )

        if label not in model_labels:
            model = apps.get_model(label)
            model_labels.add(label)
            models.append(model)

            if clean:
                puts("Removing entries for model %s" % label)
                model.objects.all().delete()

        obj.save()

    if reset:
        for app_label in app_labels:
            reset_sequence(app_label)

    if images:
        for model in models:
            for field in model._meta.fields:
                if isinstance(field, ImageField):
                    get_images(media_url, model.objects.all(), field.name)


def get_reset_command(app_label):
    app_config = apps.get_app_config(app_label)
    models = app_config.get_models(include_auto_created=True)
    statements = connection.ops.sequence_reset_sql(no_style(), models)
    return "\n".join(statements)


def reset_sequence(app_label):
    """
    Reset the primary key sequence for the tables in an application.
    This is necessary if any local edits have happened to the table.
    """

    puts("Resetting primary key sequence for {0}".format(app_label))

    cursor = connection.cursor()
    cmd = get_reset_command(app_label)
    cursor.execute(cmd)


def get_images(base_url, queryset, field):
    puts("Syncing images for %s %s" % (queryset.model.__name__, field))
    for obj in queryset:
        download(base_url, getattr(obj, field))


def download(base_url, source_image):
    if not source_image:
        return

    if os.path.exists(source_image.path):
        return

    upload_directory = os.path.dirname(source_image.path)

    if not os.path.isdir(upload_directory):
        mkdir(upload_directory)

    endpoint = "%s%s" % (base_url, source_image)

    puts("Downloading %s" % endpoint)

    response = requests.get(endpoint, stream=True)

    if not response.ok:
        puts(
            "%s response. Unable to download image." % response.status_code,
        )
        return

    with open(source_image.path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if not (e.errno == EEXIST and isdir(path)):
            raise
