import pytest

from html_checker.utils import is_file, is_url


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
    (
        "file:/foo/bar.txt",
        True,
    ),
])
def test_is_file(path, expected):
    """
    Should detect if given path is a filepath.
    """
    assert expected == is_file(path)


@pytest.mark.parametrize("path,expected", [
    (
        "http://perdu.com",
        True,
    ),
    (
        "https://perdu.com",
        True,
    ),
    (
        "/foo",
        False,
    ),
    (
        "/foo/",
        False,
    ),
    (
        "./foo",
        False,
    ),
    (
        "../foo",
        False,
    ),
    (
        "foo",
        False,
    ),
    (
        "foo/bar",
        False,
    ),
    (
        "foo/bar.txt",
        False,
    ),
    (
        "file:/foo/bar.txt",
        False,
    ),
])
def test_is_url(path, expected):
    """
    Should detect if given path is an URL.
    """
    assert expected == is_url(path)
