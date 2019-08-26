import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend


def test_site_missing_args(caplog):
    """
    Invoked without any arguments fails because it need at least a path.
    """
    runner = CliRunner()

    # Temporary isolated current dir
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, ["site"])

        assert result.exit_code == 2

        assert caplog.record_tuples == []


def test_site_invalid_sitemap_path(caplog):
    """
    When sitemap path is invalid command is aborted.
    """
    runner = CliRunner()

    # Temporary isolated current dir
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["foo.html"]

        expected = [
            ("py-html-checker", 50, "Given sitemap path does not exists: foo.html"),
        ]

        result = runner.invoke(cli_frontend, ["site"] + args)

        assert result.exit_code == 1

        assert caplog.record_tuples == expected


def test_site_invalid_item_path(caplog, settings):
    """
    When sitemap path contains invalid item filepath command is aborted.
    """
    runner = CliRunner()

    # Temporary isolated current dir
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = [os.path.join(settings.fixtures_path, "sitemap.invalidpath.xml")]

        expected = [
            ("py-html-checker", 50, "Given path does not exists: foo.html"),
            ("py-html-checker", 50, "Given path does not exists: bar.html"),
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        result = runner.invoke(cli_frontend, ["site"] + args)

        assert result.exit_code == 1

        assert caplog.record_tuples == expected
