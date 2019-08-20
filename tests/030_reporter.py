import os

from collections import OrderedDict

import pytest

from html_checker.report import LogExportBase
from html_checker.exceptions import ReportError, ExportError


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


@pytest.mark.parametrize("report,expected", [
    (
        [
            ("foo.html", [
                {
                    "type": "critical",
                    "message": "File path does not exists."
                }
            ]),
        ],
        [
            (
                'py-html-checker',
                40,
                "File path does not exists."
            )
        ],
    ),
    (
        [
            ("{FIXTURES}/html/valid.warning.html", [
                {
                    "hiliteStart": 10,
                    "type": "error",
                    "message": "End tag for  \u201cbody\u201d seen, but there were unclosed elements.",
                    "firstColumn": 1,
                    "hiliteLength": 7,
                    "extract": "\n    </p>\n</body>\n</htm",
                    "lastLine": 12,
                    "lastColumn": 7
                },
            ]),
        ],
        [
            (
                'py-html-checker',
                40,
                "File path does not exists."
            )
        ],
    ),
])
def test_build(caplog, settings, report, expected):
    """
    Expected logs should be printed to standard output for each messages
    """
    reporter = LogExportBase()

    # Rebuild report data to include fixtures path
    final_report = []
    for item_path, data in report:
        final_report.append(
            (settings.format(item_path), data)
        )

    reporter.build(OrderedDict(final_report))

    assert expected == caplog.record_tuples
