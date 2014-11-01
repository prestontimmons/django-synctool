import codecs
from setuptools import setup, find_packages
from os.path import dirname, join, realpath


ROOT = realpath(dirname(__file__))


def read(path):
    with codecs.open(join(ROOT, path), encoding="utf-8") as f:
        return f.read()


version = __import__("synctool").__version__


setup(
    name="django-synctool",
    version=version,
    url="https://github.com/prestontimmons/django-synctool",
    description="Sync data between databases.",
    long_description=read("README.rst"),
    author="Preston Timmons",
    author_email="prestontimmons@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Django>=1.7",
        "mock",
        "requests",
    ],
    classifiers=[
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
)
