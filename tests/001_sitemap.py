"""
NOTE: Ressource URLs are not tested to avoid depending from a webserver
      instance.
"""
import os

import pytest

from judas.sitemap import Sitemap

from judas.exceptions import PathInvalidError, SitemapInvalidError


@pytest.mark.parametrize("path,expected", [
    (
        "http://perdu.com",
        False,
    ),
    (
        "https://perdu.com",
        False,
    ),
    (
        "/foo",
        True,
    ),
    (
        "/foo/",
        True,
    ),
    (
        "./foo",
        True,
    ),
    (
        "../foo",
        True,
    ),
    (
        "foo",
        True,
    ),
    (
        "foo/bar",
        True,
    ),
    (
        "foo/bar.txt",
        True,
    ),
])
def test_is_file(path, expected):
    """
    Should detect if given path is an url or a filepath
    """

    s = Sitemap()

    assert expected == s.is_file(path)


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
    "http://qsmdlkqsdqsopdkqnqszzaaaAAazdqmjudas/sdflmksdlmfk",
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
    Should return urls from XML sitemap
    """
    s = Sitemap()

    filepath = os.path.join(settings.fixtures_path, path)

    ressource = s.get_file_ressource(filepath)

    assert expected == s.parse_sitemap_xml(ressource)
