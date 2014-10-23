#!/usr/bin/env python

from os import environ
environ["SYNCTOOL_TEST"] = "true"
environ["SYNCTOOL_VERBOSITY"] = "0"

from os.path import dirname, abspath
import sys

from django.conf import settings


if not settings.configured:
    settings_dict = dict(
        INSTALLED_APPS=["synctool"],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            },
        },
        ROOT_URLCONF="",
        SILENCED_SYSTEM_CHECKS = ["1_7.W001"],
    )

    settings.configure(**settings_dict)


import django
django.setup()


def runtests(test_labels):
    sys.path.insert(0, dirname(abspath(__file__)))

    from django.test.runner import DiscoverRunner
    failures = DiscoverRunner(
        verbosity=1,
        interactive=True,
        failfast=False,
    ).run_tests(test_labels)
    sys.exit(failures)


if __name__ == "__main__":
    labels = sys.argv[1:] or [
        "synctool",
    ]

    runtests(labels)
