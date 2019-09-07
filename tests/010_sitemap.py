"""
NOTE: Ressource URLs are not tested to avoid depending from a webserver
      instance.
"""
import os

import pytest
import requests

from html_checker import USER_AGENT
from html_checker.exceptions import PathInvalidError, SitemapInvalidError
from html_checker.sitemap import Sitemap


class FakeResponse:
    """
    Simulate a successful requests response
    """
    status_code = 200

    def __init__(self, *args, **kwargs):
        self.passed_args = args
        self.passed_kwargs = kwargs

    @property
    def content(self):
        return {
            "args": self.passed_args,
            "kwargs": self.passed_kwargs,
        }


def mock_requests_get(*args, **kwargs):
    """
    Mock requests get method to return a fake response object with only some
    passed values but does not perform any request.
    """
    return FakeResponse(*args, **kwargs)


@pytest.mark.parametrize("path,user_agent,expected", [
    (
        "http://perdu.com",
        None,
        {
            "args": ("http://perdu.com",),
            "kwargs": {
                "headers": {"User-Agent": USER_AGENT}
            },
        },
    ),
    (
        "http://perdu.com",
        "Foobar",
        {
            "args": ("http://perdu.com",),
            "kwargs": {
                "headers": {"User-Agent": "Foobar"}
            },
        },
    ),
])
def test_custom_user_agent(monkeypatch, path, user_agent, expected):
    """
    Default or custom user agent should be correctly set to a request
    """
    monkeypatch.setattr(requests, "get", mock_requests_get)

    s = Sitemap(user_agent=user_agent)

    response = s.get_url_ressource(path)
    print(response)
    assert expected == response


@pytest.mark.parametrize("path", [
    "foo.dqjdklqsjdlqk",
    "http://perdu.com",
    "https://perdu.com/foo.txt",
    "https://perdu.com/bar.html",
])
def test_contenttype_fail(path):
    """
    Should fail to return content-type keyword and raise exception.
    """
    s = Sitemap()

    with pytest.raises(PathInvalidError):
        s.contenttype(path)


@pytest.mark.parametrize("path,expected", [
    (
        "https://perdu.com/sitemap.xml",
        "xml",
    ),
    (
        "https://perdu.com/sitemap.json",
        "json",
    ),
    (
        "sitemap.xml",
        "xml",
    ),
    (
        "tests/data_fixtures/sitemap.xml",
        "xml",
    ),
    (
        "./sitemap.json",
        "json",
    ),
])
def test_contenttype_success(path, expected):
    """
    Should succeed to return content-type keyword
    """
    s = Sitemap()

    assert expected == s.contenttype(path)


@pytest.mark.parametrize("path", [
    "nope.txt",
    "dummy_sitemap.xml",
])
def test_get_file_ressource_fail(settings, path):
    """
    Should fail to open file and raise exception.
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    with pytest.raises(PathInvalidError):
        s.get_file_ressource(path)


@pytest.mark.parametrize("path,expected", [
    (
        "dummy.txt",
        "foo\n"
    ),
    (
        "dummy_sitemap.xml",
        "<urlset></urlset>\n"
    ),
])
def test_get_file_ressource_success(settings, path, expected):
    """
    Should open file an return its content
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    assert expected == s.get_file_ressource(filepath)


@pytest.mark.parametrize("path", [
    "nope",
    "https://google.fr/sdflmksdlmfk",
    "http://qsmdlkqsdqsopdkqnqszzaaaAAazdqmhtml_checker/sdflmksdlmfk",
])
def test_get_url_ressource_fail(path):
    """
    Should fail to open url and raise exception.
    """
    s = Sitemap()

    with pytest.raises(PathInvalidError):
        s.get_url_ressource(path)


@pytest.mark.parametrize("path", [
    "sitemap.invalid.json",
    "sitemap.malformed.json",
])
def test_parse_sitemap_json_fail(settings, path):
    """
    Should raise exception for invalid JSON sitemap
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    ressource = s.get_file_ressource(filepath)

    with pytest.raises(SitemapInvalidError):
        s.parse_sitemap_json(ressource)


@pytest.mark.parametrize("path,expected", [
    (
        "sitemap.json",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
])
def test_parse_sitemap_json_success(settings, path, expected):
    """
    Should return urls from JSON sitemap
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    ressource = s.get_file_ressource(filepath)

    assert expected == s.parse_sitemap_json(ressource)


@pytest.mark.parametrize("path", [
    "sitemap.invalid.xml",
    "sitemap.malformed.xml",
])
def test_parse_sitemap_xml_fail(settings, path):
    """
    Should raise exception for invalid XML sitemap
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    ressource = s.get_file_ressource(filepath)

    with pytest.raises(SitemapInvalidError):
        s.parse_sitemap_xml(ressource)


@pytest.mark.parametrize("path,expected", [
    (
        "sitemap.xml",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
    (
        "sitemap.nonamespace.xml",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
    (
        "sitemap.missingloc.xml",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
])
def test_parse_sitemap_xml_success(settings, path, expected):
    """
    Should correctly parse sitemap and return every urls
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    ressource = s.get_file_ressource(filepath)

    assert expected == s.parse_sitemap_xml(ressource)


@pytest.mark.parametrize("path,expected", [
    (
        "sitemap.xml",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
    (
        "sitemap.nonamespace.xml",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
    (
        "sitemap.missingloc.xml",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
    (
        "sitemap.json",
        [
            "http://perdu.com/",
            "https://www.google.com/",
        ]
    ),
])
def test_get_urls(settings, path, expected):
    """
    Should return urls from XML sitemap
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    assert expected == s.get_urls(filepath)
