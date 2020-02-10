from collections import OrderedDict

import pytest

from jinja2 import Environment, Template

from html_checker.export.jinja import JinjaExport
from html_checker.reporter import ReportStore


# A dummy exporter store to inject during tests to avoid launching
# validator+reporter
SAMPLE_REPORT = [
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
]


def test_get_jinjaenv():
    """
    Should return an instance of a 'jinja2.Environment'
    """
    exporter = JinjaExport()

    assert isinstance(exporter.get_jinjaenv(), Environment)


def test_get_template():
    """
    Every registered templates from exporter 'TEMPLATES' attribute
    should be an existing and valid template for Jinja when it try to load it.
    """
    exporter = JinjaExport()

    for k,v in exporter.TEMPLATES.items():
        assert isinstance(exporter.get_template(v), Template)


def test_validate_success():
    """
    Existing path should be valid and does not return any message.

    We just use the default path that should always be valid.
    """
    exporter = JinjaExport()

    assert exporter.validate() == False


def test_validate_notexisting():
    """
    Unexisting path should be invalid and return an error message.
    """
    exporter = JinjaExport(template_dir="/home/wrong")

    msg = "Given template directory does not exists: /home/wrong"

    assert exporter.validate() == msg


def test_validate_missing_files(settings):
    """
    Directory which misses some required templates should be invalid and return
    an error message.

    Use an existing directory from application but which is not a template
    directory.
    """
    exporter = JinjaExport(template_dir=settings.tests_dir)

    msg = ("Some required files are missing from template directory: "
           "audit.html, report.html, main.css, summary.html")

    assert exporter.validate() == msg


def test_pack_release():
    """
    In packed release mode, only one 'audit' document is created and finally the
    CSS file.

    Documents contents are not checked, just their existence and template build
    without any errors.
    """
    exporter = JinjaExport()

    # Directly fill report registry
    r = ReportStore([])
    r.registry = OrderedDict(SAMPLE_REPORT)

    exporter.build(r.registry)

    results = exporter.release(pack=True)

    assert len(results) == 2
    assert results[0]["document"] == "index.html"
    assert results[1]["document"] == "main.css"


def test_pack_release():
    """
    In un packed release mode, a 'report' document is created for each report
    then a 'summary' document is created and finally the CSS file.

    Documents contents are not checked, just their existence and template build
    without any errors.
    """
    exporter = JinjaExport()

    # Directly fill report registry
    r = ReportStore([])
    r.registry = OrderedDict(SAMPLE_REPORT)

    exporter.build(r.registry)

    results = exporter.release(pack=False)

    assert len(results) == 6
    assert results[0]["document"] == "path-1.html"
    assert results[1]["document"] == "path-2.html"
    assert results[2]["document"] == "path-3.html"
    assert results[3]["document"] == "path-4.html"
    assert results[4]["document"] == "index.html"
    assert results[5]["document"] == "main.css"
