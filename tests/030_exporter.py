import logging
import os

from collections import OrderedDict

import pytest

from html_checker.export import LogExportBase
from html_checker.exceptions import ReportError, ExportError
from html_checker.reporter import ReportStore


@pytest.mark.parametrize("row,expected", [
    (
        {},
        None,
    ),
    (
        {
            "extract": "foo",
            "firstLine": "bar",
            "firstColumn": "ping",
            "lastColumn": "pong",
        },
        None,
    ),
    (
        {
            "firstLine": "foo",
            "lastLine": "bar",
            "firstColumn": "ping",
            "lastColumn": "pong",
        },
        "From line foo column ping to line bar column pong",
    ),
    (
        {
            "lastLine": "bar",
            "firstColumn": "ping",
            "lastColumn": "pong",
        },
        "From line bar column ping to line bar column pong",
    ),
])
def test_format_source_position(row, expected):
    """
    Format source position should support every cases.
    """
    reporter = LogExportBase()

    assert expected == reporter.format_source_position(row)


@pytest.mark.parametrize("report,level,expected", [
    (
        [
            ("/html/foo.html", [
                {
                    "type": "info",
                    "message": "This is an info.",
                },
            ]),
        ],
        "DEBUG",
        [
            ("py-html-checker", logging.DEBUG, "====="),
            (
                "py-html-checker",
                logging.INFO,
                "/html/foo.html"
            ),
            ("py-html-checker", logging.DEBUG, "-"),
            (
                "py-html-checker",
                logging.DEBUG,
                "This is an info."
            ),
        ],
    ),
    (
        [
            ("/html/foo.html", None),
            ("/html/bar.html", None),
        ],
        "DEBUG",
        [
            ("py-html-checker", logging.DEBUG, "====="),
            (
                "py-html-checker",
                logging.INFO,
                "/html/foo.html"
            ),
            (
                "py-html-checker",
                logging.DEBUG,
                "There was not any log report for this path."
            ),
            ("py-html-checker", logging.DEBUG, "====="),
            (
                "py-html-checker",
                logging.INFO,
                "/html/bar.html"
            ),
            (
                "py-html-checker",
                logging.DEBUG,
                "There was not any log report for this path."
            ),
        ],
    ),
    (
        [
            ("foo.html", [
                {
                    "type": "critical",
                    "message": "File path does not exists."
                }
            ]),
        ],
        "WARNING",
        [
            (
                "py-html-checker",
                logging.ERROR,
                "File path does not exists."
            )
        ],
    ),
    (
        [
            ("/html/foo.html", [
                {
                    "type": "error",
                    "lastLine": 10,
                    "firstColumn": 1,
                    "lastColumn": 2,
                    "message": "This is an error.",
                    "extract": "<some html>",
                },
            ]),
        ],
        "WARNING",
        [
            (
                "py-html-checker",
                logging.ERROR,
                "From line 10 column 1 to line 10 column 2"
            ),
            (
                "py-html-checker",
                logging.ERROR,
                "This is an error."
            ),
            (
                "py-html-checker",
                logging.ERROR,
                "<some html>"
            ),
        ],
    ),
    (
        [
            ("/html/foo.html", [
                {
                    "type": "info",
                    "subType": "warning",
                    "message": "This is a warning.",
                },
            ]),
        ],
        "WARNING",
        [
            (
                "py-html-checker",
                logging.WARNING,
                "This is a warning."
            ),
        ],
    ),
    (
        [
            ("/html/foo.html", [
                {
                    "type": "error",
                    "firstLine": 10,
                    "lastLine": 20,
                    "firstColumn": 1,
                    "lastColumn": 2,
                    "message": "This\nis\ran\terror.",
                    "extract": "<some html>",
                },
            ]),
        ],
        "WARNING",
        [
            (
                "py-html-checker",
                logging.ERROR,
                "From line 10 column 1 to line 20 column 2"
            ),
            (
                "py-html-checker",
                logging.ERROR,
                "This\nis\ran\terror."
            ),
            (
                "py-html-checker",
                logging.ERROR,
                "<some html>"
            ),
        ],
    ),
])
def test_build(caplog, report, level, expected):
    """
    Expected logs should be printed to standard output for each messages and
    depending the setted logging level.
    """
    caplog.set_level(level, logger="py-html-checker")

    exporter = LogExportBase()

    # Directly file report registry
    r = ReportStore([])
    r.registry = OrderedDict(report)

    exporter.build(r.registry)

    #print(caplog.record_tuples)

    assert expected == caplog.record_tuples


def test_build_disabled_dividers(caplog):
    """
    Expect logs without any divider
    """
    caplog.set_level(logging.DEBUG, logger="py-html-checker")

    exporter = LogExportBase(dividers={})

    # Directly file report registry
    r = ReportStore([])
    r.registry = OrderedDict([
        ("/html/foo.html", [
            {
                "type": "info",
                "message": "This is an info.",
            },
        ]),
    ])

    exporter.build(r.registry)

    #print(caplog.record_tuples)

    expected = [
        (
            "py-html-checker",
            logging.INFO,
            "/html/foo.html"
        ),
        (
            "py-html-checker",
            logging.DEBUG,
            "This is an info."
        ),
    ]

    assert expected == caplog.record_tuples
