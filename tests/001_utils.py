import io
import json
import pytest

from html_checker.exceptions import HtmlCheckerBaseException
from html_checker.utils import (is_local_ressource, is_url, reduce_unique,
                                merge_compute, resolve_paths, write_documents,
                                format_hostname)


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
def test_is_local_ressource(path, expected):
    """
    Should detect if given path is a filepath.
    """
    assert expected == is_local_ressource(path)


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


@pytest.mark.parametrize("items,expected", [
    (
        ["a"],
        ["a"],
    ),
    (
        ["a", "b"],
        ["a", "b"],
    ),
    (
        [3, 2, 4, 1],
        [3, 2, 4, 1],
    ),
    (
        [3, 2, 4, 2, 1],
        [3, 2, 4, 1],
    ),
    (
        [3, 4, 4, 2, 1],
        [3, 4, 2, 1],
    ),
    (
        ["f", "o", "o", "b", "a", "r", "b", "a", "r"],
        ["f", "o", "b", "a", "r"],
    ),
])
def test_reduce_unique(items, expected):
    """
    Given list should be reduced to a list of unique values, respecting
    original order.
    """
    assert expected == reduce_unique(items)


@pytest.mark.parametrize("left_dict,right_dict,expected", [
    (
        {},
        {},
        {},
    ),
    (
        {
            "foo": 1,
            "bar": 0,
        },
        {
            "foo": 1,
            "bar": 1,
        },
        {
            "foo": 2,
            "bar": 1,
        },
    ),
    (
        {
            "foo": 1,
            "bar": 0,
            "ping": "pong",
            "yellow": True,
            "fang": "shui",
            "ying": 1,
            "Nope": None,
        },
        {
            "foo": 1,
            "bar": 1,
            "fang": 0,
            "yellow": False,
            "fang": 0,
            "ying": "yang",
        },
        {
            "foo": 2,
            "bar": 1,
            "ping": "pong",
            "yellow": True,
            "fang": "shui",
            "ying": 1,
            "Nope": None,
        },
    ),
])
def test_merge_compute(left_dict, right_dict, expected):
    """
    Given left and right dict should be merged as expected.
    """
    assert expected == merge_compute(left_dict, right_dict)


@pytest.mark.parametrize("paths,expected", [
    (
        [
            "foo.html",
        ],
        "{PACKAGE}/foo.html",
    ),
    (
        [
            ".",
            "foo.html",
        ],
        "{PACKAGE}/foo.html",
    ),
    (
        [
            ".",
            "bar/../foo.html",
        ],
        "{PACKAGE}/foo.html",
    ),
    (
        [
            "/home/foo",
            "foo.html",
        ],
        "/home/foo/foo.html",
    ),
    (
        [
            "~",
            "foo.html",
        ],
        "{HOMEDIR}/foo.html",
    ),
    (
        [
            ".",
            "foo/~bar/ping.html",
        ],
        "{PACKAGE}/foo/~bar/ping.html",
    ),
])
def test_resolve_paths(settings, paths, expected):
    """
    Given path should be combined correctly to an absolute normalized path.
    """
    assert settings.format(expected) == resolve_paths(*paths)


@pytest.mark.parametrize("documents,expected", [
    (
        [
            {
                "document": "foo.html",
                "content": "<html><foo>bar</foo></html>",
            },
        ],
        ["{TMPDIR}/foo.html"],
    ),
    (
        [
            {
                "document": "bar.html",
                "content": "<html><bar>foo</bar></html>",
            },
            {
                "document": "ping.json",
                "content": json.dumps({"ping": "pong", "blah": True}),
            },
        ],
        [
            "{TMPDIR}/bar.html",
            "{TMPDIR}/ping.json",
        ],
    ),
])
def test_write_documents(temp_builds_dir, documents, expected):
    """
    Given documents should be written into destination directory.

    NOTE: Every files are created in the same temp directory, so take caution
    to use different files from all tests parametrizes.
    """
    destination = temp_builds_dir.join('write_documents').strpath

    docs = write_documents(destination, documents)

    assert [item.format(TMPDIR=destination) for item in expected] == docs

    # Check writed files contents
    for doc in documents:
        with io.open(resolve_paths(destination, doc["document"]), 'r') as fp:
            content = fp.read()
        assert content == doc["content"]



@pytest.mark.parametrize("value,expected", [
    (
        "foo",
        ("foo", 8002),
    ),
    (
        "foo:",
        ("foo", 8002),
    ),
    (
        "foo:80",
        ("foo", 80),
    ),
    (
        "foo:80:bar",
        ("foo", 80),
    ),
    (
        "0.0.0.0",
        ("0.0.0.0", 8002),
    ),
    (
        "0.0.0.0:80",
        ("0.0.0.0", 80),
    ),
])
def test_format_hostname_success(value, expected):
    """
    Valid hostnames should be validated and returned in a tuple either with
    given port or the default one.
    """
    assert expected == format_hostname(value)



@pytest.mark.parametrize("value,expected", [
    (
        "",
        "Given server hostname is empty.",
    ),
    (
        ":",
        "Given server hostname is empty.",
    ),
    (
        ":80",
        "Given server hostname is empty.",
    ),
    (
        "foo:bar",
        "Given server port number is invalid.",
    ),
])
def test_format_hostname_fail(value, expected):
    """
    Valid hostnames should be validated and returned in a tuple either with
    given port or the default one.
    """
    with pytest.raises(HtmlCheckerBaseException) as excinfo:
        format_hostname(value)

    assert expected == str(excinfo.value)
