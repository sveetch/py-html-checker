import pytest

from collections import OrderedDict

from jinja2 import Environment, Template

from html_checker.export import JinjaExport
from html_checker.reporter import ReportStore


def test_get_jinjaenv():
    """
    Should return an instance of a 'jinja2.Environment'
    """
    exporter = JinjaExport()

    assert isinstance(exporter.get_jinjaenv(), Environment)


def test_get_template():
    """
    Should return an instance of a 'jinja2.Template'
    """
    exporter = JinjaExport()

    result = exporter.get_template("basic.html")

    assert isinstance(result, Template)


@pytest.mark.parametrize("row,expected", [
    (
        {
            "type": "info",
            "message": "This is an info.",
        },
        {
            "type": "info",
            "source": {},
            "message": "This is an info."
        },
    ),
    (
        {
            "type": "error",
            "message": "This\nis\ran\terror.",
            "extract": "<some html>",
        },
        {
            "type": "error",
            "source": {
                "extract": "<some html>",
            },
            "message": "This\nis\ran\terror."
        },
    ),
    (
        {
            "type": "info",
            "subType": "warning",
            "message": "This is a warning.",
        },
        {
            "type": "warning",
            "source": {},
            "message": "This is a warning.",
        },
    ),
    (
        {
            "type": "error",
            "firstLine": 10,
            "lastLine": 20,
            "firstColumn": 1,
            "lastColumn": 2,
            "message": "This\nis\ran\terror.",
            "extract": "<some html>",
        },
        {
            "type": "error",
            "source": {
                "linestart": 10,
                "colstart": 1,
                "colend": 2,
                "extract": "<some html>",
                "lineend": 20
            },
            "message": "This\nis\ran\terror."
        },
    ),
    (
        {
            "type": "error",
            "firstLine": 10,
            "lastLine": 20,
            "firstColumn": 1,
            "lastColumn": 2,
            "message": "This\nis\ran\terror.",
        },
        {
            "type": "error",
            "source": {
                "linestart": 10,
                "colstart": 1,
                "colend": 2,
                "extract": None,
                "lineend": 20
            },
            "message": "This\nis\ran\terror."
        },
    ),
])
def test_format_row(caplog, row, expected):
    """
    ..
    """
    caplog.set_level("DEBUG", logger="py-html-checker")

    exporter = JinjaExport()

    result = exporter.format_row("dummy.html", row)

    assert expected == result


@pytest.mark.parametrize("report,expected", [
    # Basic sample
    (
        [
            ("/html/foo.html", [
                {
                    "type": "info",
                    "message": "This is an info.",
                },
            ]),
        ],
        {
            "items": [
                (
                    "/html/foo.html",
                    [
                        {
                            "type": "info",
                            "source": {},
                            "message": "This is an info."
                        }
                    ]
                )
            ],
        },
    ),
    # Complete sample
    (
        [
            ("http://nope", None),
            ("/html/foo.html", [
                {
                    "type": "info",
                    "message": "This is an info.",
                },
            ]),
            ("/html/wrong.html", [
                {
                    "type": "error",
                    "message": "This\nis\ran\terror.",
                    "extract": "<some html>",
                },
            ]),
            ("/html/verybad.html", [
                {
                    "type": "info",
                    "subType": "warning",
                    "message": "1. This is a warning.",
                },
                {
                    "type": "warning",
                    "message": "2. This is a warning which should never occurs from vnu.",
                },
                {
                    "type": "error",
                    "message": "3. This is a basic error.",
                },
                {
                    "type": "error",
                    "firstLine": 10,
                    "lastLine": 20,
                    "firstColumn": 1,
                    "lastColumn": 2,
                    "message": "4. This\nis\ran\terror.",
                    "extract": "<some html>",
                },
            ]),
        ],
        {
            "items": [
                (
                    "http://nope",
                    [
                        {
                            "type": "debug",
                            "message": "There was not any log report for this path."
                        }
                    ]
                ),
                (
                    "/html/foo.html",
                    [
                        {
                            "type": "info",
                            "message": "This is an info.",
                            "source": {}
                        }
                    ]
                ),
                (
                    "/html/wrong.html",
                    [
                        {
                            "type": "error",
                            "message": "This\nis\ran\terror.",
                            "source": {
                                "extract": "<some html>"
                            }
                        }
                    ]
                ),
                (
                    "/html/verybad.html",
                    [
                        {
                            "type": "warning",
                            "message": "1. This is a warning.",
                            "source": {}
                        },
                        {
                            "type": "warning",
                            "message": "2. This is a warning which should never occurs from vnu.",
                            "source": {}
                        },
                        {
                            "type": "error",
                            "message": "3. This is a basic error.",
                            "source": {}
                        },
                        {
                            "type": "error",
                            "message": "4. This\nis\ran\terror.",
                            "source": {
                                "colend": 2,
                                "lineend": 20,
                                "extract": "<some html>",
                                "linestart": 10,
                                "colstart": 1
                            }
                        }
                    ]
                )
            ],
        },
    ),
])
def test_build(caplog, report, expected):
    """
    ...
    """
    caplog.set_level("DEBUG", logger="py-html-checker")

    exporter = JinjaExport()

    # Directly fill report registry
    r = ReportStore([])
    r.registry = OrderedDict(report)

    exporter.build(r.registry)

    #import json
    #print(json.dumps(exporter.render_context, indent=4, default=str))

    # Drop created datetime since runned test cannot know it
    del exporter.render_context["created"]

    assert expected == exporter.render_context

    #assert 1 == 42

def test_release_one(caplog):
    """
    ...
    """
    caplog.set_level("DEBUG", logger="py-html-checker")

    report = [
        ("/html/foo.html", [
            {
                "type": "info",
                "message": "This is an info.",
            },
        ]),
    ]

    exporter = JinjaExport()

    # Directly fill report registry
    r = ReportStore([])
    r.registry = OrderedDict(report)

    exporter.build(r.registry)
    html = exporter.release()
    print(html)

    assert html == ""

