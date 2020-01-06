import pytest

from jinja2 import Environment, Template

from html_checker.export.jinja import JinjaExport


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
