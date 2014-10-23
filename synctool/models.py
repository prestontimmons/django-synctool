from os import environ

from django.db import models


if environ.get("SYNCTOOL_TEST"):

    class Blog(models.Model):
        slug = models.SlugField()
        categories = models.ManyToManyField(
            "synctool.Category", blank=True,
        )

    class Post(models.Model):
        blog = models.ForeignKey("synctool.Blog")
        slug = models.SlugField()

    class Category(models.Model):
        slug = models.SlugField(max_length=150)

    class Person(models.Model):
        photo = models.ImageField(upload_to="photos")
