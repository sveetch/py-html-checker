import pytest

from html_checker.utils import (is_local_ressource, is_url, reduce_unique,
                                merge_compute)


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

    """
    assert expected == merge_compute(left_dict, right_dict)
