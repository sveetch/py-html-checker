import json
import pytest

from html_checker.export.json import JsonExport


def test_render():
    """
    Render should return a dict with document name (as "document" item) and
    document context (as "content" item).
    """
    data = {
        "document": "foo.html",
        "context": {
            "name": "/html/foo.html",
        },
    }

    expected = {
        "document": "foo.html",
        "content": "{\"name\": \"/html/foo.html\"}",
    }

    # Remove indentation for more compact results for assertion
    exporter = JsonExport(indent=None)

    doc = exporter.render(data)

    print()
    print(json.dumps(doc, indent=4, default=str))
    print()

    assert doc == expected


@pytest.mark.parametrize("pack,expected", [
    (
        True,
        [
            {
                "document": "audit.json",
                "content": {
                    "kind": "audit",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "foo": 1,
                        "ping": 1,
                        "nope": 0,
                        "bar": 1,
                        "toast": 3
                    },
                    "data": None,
                    "paths": [
                        {
                            "data": {
                                "messages": "Dummy foo"
                            },
                            "statistics": {
                                "foo": 1,
                                "nope": 0,
                                "toast": 1
                            },
                            "name": "/html/foo.html"
                        },
                        {
                            "data": {
                                "messages": "Dummy bar"
                            },
                            "statistics": {
                                "nope": 0,
                                "bar": 1,
                                "toast": 1
                            },
                            "name": "/html/bar.html"
                        },
                        {
                            "data": {
                                "messages": "Dummy ping"
                            },
                            "statistics": {
                                "ping": 1,
                                "nope": 0,
                                "toast": 1
                            },
                            "name": "http://ping"
                        }
                    ],
                },
            }
        ],
    ),
    (
        False,
        [
            {
                "document": "path-1.json",
                "content": {
                    "name": "/html/foo.html",
                    "kind": "report",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "nope": 0,
                        "foo": 1,
                        "toast": 1
                    },
                    "data": {
                        "messages": "Dummy foo"
                    },
                }
            },
            {
                "document": "path-2.json",
                "content": {
                    "name": "/html/bar.html",
                    "kind": "report",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "nope": 0,
                        "bar": 1,
                        "toast": 1
                    },
                    "data": {
                        "messages": "Dummy bar"
                    },
                }
            },
            {
                "document": "path-3.json",
                "content": {
                    "name": "http://ping",
                    "kind": "report",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "nope": 0,
                        "toast": 1,
                        "ping": 1
                    },
                    "data": {
                        "messages": "Dummy ping"
                    },
                }
            },
            {
                "document": "summary.json",
                "content": {
                    "kind": "summary",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "nope": 0,
                        "toast": 3,
                        "bar": 1,
                        "foo": 1,
                        "ping": 1
                    },
                    "paths": [
                        {
                            "statistics": {
                                "nope": 0,
                                "foo": 1,
                                "toast": 1
                            },
                            "name": "/html/foo.html",
                            "path": "path-1.json"
                        },
                        {
                            "statistics": {
                                "nope": 0,
                                "bar": 1,
                                "toast": 1
                            },
                            "name": "/html/bar.html",
                            "path": "path-2.json"
                        },
                        {
                            "statistics": {
                                "nope": 0,
                                "toast": 1,
                                "ping": 1
                            },
                            "name": "http://ping",
                            "path": "path-3.json"
                        }
                    ]
                }
            }
        ],
    ),
])
def test_release(pack, expected):
    """
    In single release mode, only one document with all reports should be
    returned.

    In multiple files mode, there should be a document for each path report
    and an index of all documents.
    """
    # Remove indentation for more compact results for assertion
    exporter = JsonExport(indent=None)

    # Dummy store payload
    exporter.store = {
        "metas": {
            "pac": "man",
        },
        "statistics": {},
        "reports": [
            (
                "/html/foo.html",
                {
                    "statistics": {
                        "toast": 1,
                        "foo": 1,
                        "nope": 0,
                    },
                    "messages": "Dummy foo",
                }
            ),
            (
                "/html/bar.html",
                {
                    "statistics": {
                        "toast": 1,
                        "bar": 1,
                        "nope": 0,
                    },
                    "messages": "Dummy bar",
                }
            ),
            (
                "http://ping",
                {
                    "statistics": {
                        "toast": 1,
                        "ping": 1,
                        "nope": 0,
                    },
                    "messages": "Dummy ping",
                }
            ),
        ],
    }

    results = exporter.release(pack=pack)

    assert len(results) == len(expected)

    # Compare result content (reversed to Python object from JSON) to expected
    # content (we need to compare Python objects since arbitrary order is
    # serialized by JSON encoder)
    for i, item in enumerate(results, start=0):
        #print("-", item["document"])
        #print(json.dumps(json.loads(item["content"]), indent=4, default=str))
        #print()
        assert item["document"] == expected[i]["document"]
        assert json.loads(item["content"]) == expected[i]["content"]
