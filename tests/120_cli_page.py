import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend


def test_page_missing_args(caplog):
    """
    Invoked without any arguments fails because it need at least a path.
    """
    runner = CliRunner()

    # Temporary isolated current dir
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, ["page"])

        assert result.exit_code == 2

        assert caplog.record_tuples == []


def test_page_invalid_paths(caplog, settings):
    """
    When there is one or more invalid path, command is aborted even if there
    are some valid path.
    """
    runner = CliRunner()

    # Temporary isolated current dir
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["foo.html", "bar.html", "{FIXTURES}/html/",
                "{FIXTURES}/html/valid.basic.html"]
        args = [settings.format(item) for item in args]

        expected = [
            ("py-html-checker", 50, "Given path does not exists: foo.html"),
            ("py-html-checker", 50, "Given path does not exists: bar.html"),
            ("py-html-checker", 50, "Directory path are not supported: {FIXTURES}/html/")
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        result = runner.invoke(cli_frontend, ["page"] + args)

        assert result.exit_code == 1

        assert caplog.record_tuples == expected


def test_page_valid_paths(caplog, settings):
    """
    Successful basic report
    """
    runner = CliRunner()

    # Temporary isolated current dir
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["{FIXTURES}/html/valid.basic.html"]
        args = [settings.format(item) for item in args]

        expected = [
            ("py-html-checker", 20, "{FIXTURES}/html/valid.basic.html"),
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        result = runner.invoke(cli_frontend, ["page"] + args)

        assert result.exit_code == 0

        assert caplog.record_tuples == expected
