import pytest

from html_checker.exceptions import ExportError
from html_checker.export import get_exporter
from html_checker.export.base import ExporterBase


@pytest.mark.parametrize("name,expected", [
    (
        "logging",
        "LoggingExport",
    ),
    (
        "html",
        "JinjaExport",
    ),
])
def test_get_exporter_success(name, expected):
    """
    'get_exporter' should return the right exporter class accorded to given
    format name.
    """
    exporter = get_exporter(name)

    assert exporter.klassname == expected


def test_get_exporter_fail():
    """
    'get_exporter' should raise an exception when given format name is not
    registered in any available exporter.
    """
    expected = "There is no exporter with format name 'nope'"

    with pytest.raises(ExportError) as excinfo:
        get_exporter("nope")

    assert expected == str(excinfo.value)


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
        {
            'colend': 'pong',
            'colstart': 'ping',
            'lineend': 'bar',
            'linestart': 'foo'
        },
    ),
    (
        {
            "lastLine": "bar",
            "firstColumn": "ping",
            "lastColumn": "pong",
        },
        {
            'colend': 'pong',
            'colstart': 'ping',
            'lineend': 'bar',
            'linestart': 'bar'
        },
    ),
])
def test_format_source_position(row, expected):
    """
    Format source position should support every cases.
    """
    reporter = ExporterBase()

    assert expected == reporter.format_source_position(row)


@pytest.mark.parametrize("row,expected_level,expected_content", [
    (
        {
            "type": "info",
            "message": "This is an info.",
        },
        'info',
        {
            'type': 'info',
            "message": "This is an info.",
        },
    ),
    (
        {
            "type": "info",
            "subType": "warning",
            "message": "This is a warning.",
        },
        'warning',
        {
            'type': 'warning',
            'message': 'This is a warning.'
        },
    ),
    (
        {
            "type": "error",
            "message": "This is an error.",
            "extract": "<some html>",
        },
        'error',
        {
            "type": "error",
            "message": "This is an error.",
            "extract": "<some html>",
        },
    ),
    (
        {
            "type": "non-document-error",
            "message": "This is a non document error.",
        },
        'error',
        {
            "type": "error",
            "message": "This is a non document error.",
        },
    ),
])
def test_parse_row_level(row, expected_level, expected_content):
    """
    Parsed row should return the right content
    """
    reporter = ExporterBase()

    level, content = reporter.parse_row_level("dummy.html", row)

    assert expected_level == level
    assert expected_content == content
