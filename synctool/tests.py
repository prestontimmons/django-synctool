from base64 import b64encode
from os.path import dirname, join, realpath
import shutil

from django.core.files import File
from django.core.serializers import deserialize
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from mock import patch
import requests

from .client import Client
from .functions import get_images, sync_data
from .models import Blog, Category, Person, Post
from .routing import Route, serialize_querysets


ROOT = realpath(dirname(__file__))
UPLOADS = join(ROOT, "uploads")
IMG = join(ROOT, "img.gif")


route = Route(api_token="token")


def authorization(token="token"):
    auth = token + ":"
    try:
        auth = bytes(auth, encoding="utf-8")
    except TypeError:
        pass
    return "Basic %s" % b64encode(auth)


blog_app = route.app("blogs", "synctool")


@route.queryset("blog-single")
def blog_single():
    return Blog.objects.all()


@route.queryset("blog-multiple")
def blog_multiple():
    return [
        Blog.objects.all(),
        Post.objects.all(),
    ]


class RouteTest(TestCase):
    urls = route.urlpatterns

    def test_single(self):
        blog = Blog.objects.create(slug="blog")

        request = RequestFactory().get("/")
        request.META["HTTP_AUTHORIZATION"] = authorization()

        response = blog_single(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response._headers["content-type"][1],
            "application/json",
        )

        data = deserialize("json", response.content)
        self.assertEqual(next(data).object, blog)

    def test_multiple(self):
        blog = Blog.objects.create(slug="blog")
        post = Post.objects.create(blog=blog, slug="slug")

        request = RequestFactory().get("/")
        request.META["HTTP_AUTHORIZATION"] = authorization()

        response = blog_multiple(request)

        self.assertEqual(response.status_code, 200)

        data = deserialize("json", response.content)

        self.assertEqual(next(data).object, blog)
        self.assertEqual(next(data).object, post)

    def test_app(self):
        blog = Blog.objects.create(slug="blog")
        post = Post.objects.create(blog=blog, slug="slug")

        request = RequestFactory().get("/")
        request.META["HTTP_AUTHORIZATION"] = authorization()

        response = blog_app(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response._headers["content-type"][1],
            "application/json",
        )

        data = deserialize("json", response.content)

        self.assertEqual(next(data).object, blog)
        self.assertEqual(next(data).object, post)

    def test_bad_authorization(self):
        request = RequestFactory().get("/")
        request.META["HTTP_AUTHORIZATION"] = authorization(token="bad")

        response = self.client.get("/blog-single/")
        self.assertEqual(response.status_code, 401)


class Response(object):

    def __init__(self, content="", ok=True, status_code=200):
        self.ok = ok
        self.content = content
        self.status_code = status_code

    def iter_content(self, buffer_size):
        return [self.content]


def blog_response():
    blog = Blog.objects.create(slug="blog")
    category = Category.objects.create(slug="category")
    blog.categories.add(category)

    querysets = [
        Category.objects.all(),
        Blog.objects.all(),
    ]

    return Response(
        content=serialize_querysets(querysets),
    )


def image_response():
    with open(IMG, mode="rb") as f:
        content = f.read()

    return Response(
        content=content,
    )


def person_response():
    Person.objects.create(photo="photos/img.gif")
    return Response(
        content=serialize_querysets(Person.objects.all())
    )


def smart_response(*args, **kwargs):
    if kwargs.get("stream"):
        return image_response()
    return person_response()


@override_settings(MEDIA_ROOT=UPLOADS)
class SyncTest(TestCase):

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(UPLOADS, ignore_errors=True)

    @patch.object(requests, "get")
    def test_sync(self, get):
        get.return_value = blog_response()
        Blog.objects.all().delete()
        Category.objects.all().delete()

        sync_data("/<url>/", "abcdef")

        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 1)

    @patch.object(requests, "get")
    def test_clean(self, get):
        get.return_value = blog_response()

        sync_data("/<url>/", "abcdef", clean=True)

        self.assertEqual(Blog.objects.count(), 1)

    @patch.object(requests, "get")
    def test_http_error(self, get):
        get.return_value = Response(ok=False, status_code=500)

        with self.assertRaises(RuntimeError):
            sync_data("/<url>/", "abcdef")

    @patch.object(requests, "get", smart_response)
    def test_images(self):
        sync_data("/<url>/", "abcdef", images=True)

        person = Person.objects.get()
        self.assertTrue(person.photo.size)


@override_settings(MEDIA_ROOT=UPLOADS)
class GetImagesTest(TestCase):

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(UPLOADS, ignore_errors=True)

    @patch.object(requests, "get")
    def test_get(self, get):
        person = Person.objects.create()
        person.photo = "photos/img.gif"
        person.save()

        get.return_value = image_response()

        get_images(
            base_url="http://127.0.0.1",
            queryset=Person.objects.all(),
            field="photo",
        )

        person = Person.objects.get()
        self.assertTrue(person.photo.size)

    @patch.object(requests, "get")
    def test_catch_bad_response(self, get):
        person = Person.objects.create()
        person.photo = "photos/img.gif"
        person.save()

        get.return_value = Response(ok=False)

        get_images(
            base_url="http://127.0.0.1",
            queryset=Person.objects.all(),
            field="photo",
        )

    @patch.object(requests, "get")
    def test_skip_if_not_defined(self, get):
        Person.objects.create()

        get_images(
            base_url="http://127.0.0.1",
            queryset=Person.objects.all(),
            field="photo",
        )

        self.assertFalse(get.called)

    @patch.object(requests, "get")
    def test_skip_if_exists(self, get):
        person = Person.objects.create()
        person.photo.save("photos/img.gif", File(open(IMG, mode="rb")))
        person.save()

        get_images(
            base_url="http://127.0.0.1",
            queryset=Person.objects.all(),
            field="photo",
        )

        self.assertFalse(get.called)


class ClientTest(TestCase):

    @patch.object(requests, "get")
    def test_sync(self, get):
        get.return_value = blog_response()
        Blog.objects.all().delete()
        Category.objects.all().delete()

        client = Client(
            api_url="http://127.0.0.1/sync/",
            api_token="token",
            media_url="http://127.0.0.1/uploads/",
        )

        client.sync("/<url>/")

        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 1)
