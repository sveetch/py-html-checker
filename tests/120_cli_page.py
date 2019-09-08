import logging
import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend


def test_page_missing_args(caplog):
    """
    Invoked without any arguments fails because it need at least a path.
    """
    runner = CliRunner()
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
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["foo.html", "bar.html", "{FIXTURES}/html/",
                "{FIXTURES}/html/valid.basic.html"]
        args = [settings.format(item) for item in args]

        expected = [
            ("py-html-checker", logging.CRITICAL, "Given path does not exists: foo.html"),
            ("py-html-checker", logging.CRITICAL, "Given path does not exists: bar.html"),
            ("py-html-checker", logging.CRITICAL, "Directory path are not supported: {FIXTURES}/html/")
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        result = runner.invoke(cli_frontend, ["page"] + args)

        assert result.exit_code == 1

        assert caplog.record_tuples == expected


def test_page_safe_invalid_paths(caplog, settings):
    """
    Safe option avoid to abort script on invalid paths.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["--safe", "foo.html", "bar.html", "{FIXTURES}/html/",
                "{FIXTURES}/html/valid.basic.html"]
        args = [settings.format(item) for item in args]

        expected = [
            ("py-html-checker", logging.CRITICAL, "Given path does not exists: foo.html"),
            ("py-html-checker", logging.CRITICAL, "Given path does not exists: bar.html"),
            ("py-html-checker", logging.CRITICAL, "Directory path are not supported: {FIXTURES}/html/")
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        # Lower logger to CRTITICAL only, this test doesnt need to check everything
        result = runner.invoke(cli_frontend, ["-v", "1", "page"] + args)

        print()
        print(result.output)
        print()
        print(result.exception)
        print()
        print(caplog.record_tuples)
        print()

        assert result.exit_code == 0

        assert caplog.record_tuples == expected


def test_page_valid_paths(caplog, settings):
    """
    Successful basic report
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["{FIXTURES}/html/valid.basic.html"]
        args = [settings.format(item) for item in args]

        expected = [
            ("py-html-checker", logging.INFO, "{FIXTURES}/html/valid.basic.html"),
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        result = runner.invoke(cli_frontend, ["page"] + args)

        assert result.exit_code == 0

        assert caplog.record_tuples == expected
