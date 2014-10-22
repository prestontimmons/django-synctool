from setuptools import setup, find_packages

DESCRIPTION = """
A tool to sync querysets between databases.
"""


setup(
    name="django-synctool",
    version="0.0",
    description="Sync querysets between databases.",
    long_description=DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)
