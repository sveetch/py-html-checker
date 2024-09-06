import logging
import os

from click.testing import CliRunner

from html_checker.cli.entrypoint import cli_frontend
from html_checker.exceptions import HtmlCheckerBaseException
from html_checker.validator import ValidatorInterface


def mock_validator_execute_validator_for_base_exception(*args, **kwargs):
    """
    Always raise a basic exception "HtmlCheckerBaseException".
    """
    raise HtmlCheckerBaseException("This is a basic exception.")


def test_site_missing_args(caplog):
    """
    Invoked without any arguments fails because it need at least a path.
    """
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(cli_frontend, ["site"])

        assert result.exit_code == 2
        assert caplog.record_tuples == []


def test_site_invalid_sitemap_path(caplog):
    """
    When sitemap path is invalid command is aborted.
    """
    runner = CliRunner()

    with runner.isolated_filesystem():
        args = ["foo.html"]

        expected = [
            (
                "py-html-checker",
                logging.CRITICAL,
                "Given sitemap path does not exists: foo.html"
            ),
        ]

        result = runner.invoke(cli_frontend, ["site"] + args)

        assert result.exit_code == 1
        assert caplog.record_tuples == expected


def test_site_invalid_item_path(caplog, settings):
    """
    If sitemap path contains invalid item filepath command is
    NOT aborted and continue to the next item.
    """
    runner = CliRunner()

    with runner.isolated_filesystem():
        args = [
            "--safe",
            os.path.join(settings.fixtures_path, "sitemap.invalidpath.xml")
        ]

        result = runner.invoke(cli_frontend, ["site"] + args)

        assert result.exit_code == 0

        assert (
            "py-html-checker",
            logging.ERROR,
            "Given path does not exists: foo.html"
        ) in caplog.record_tuples
        assert (
            "py-html-checker",
            logging.ERROR,
            "Given path does not exists: bar.html"
        ) in caplog.record_tuples

        assert len(caplog.record_tuples) > 2


def test_site_nosafe_exception(monkeypatch, caplog, settings):
    """
    With safe mode not enabled, internal exception should not be catched and
    abort program execution.

    Use a mockup to force validator.execute_validator() method to raise a basic
    internal exception.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator_for_base_exception)

    runner = CliRunner()

    with runner.isolated_filesystem():
        args = [os.path.join(settings.fixtures_path, "sitemap.xml")]

        result = runner.invoke(cli_frontend, ["site"] + args)

        assert isinstance(result.exception, HtmlCheckerBaseException) is True
        assert result.exit_code == 1


def test_site_safe_exception(monkeypatch, caplog, settings):
    """
    With safe mode enabled internal exceptions should be catched and don't
    abort execution.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator_for_base_exception)

    expected = [
        ("py-html-checker", logging.INFO, "Sitemap have 2 paths"),
        ("py-html-checker", logging.INFO, "http://perdu.com/"),
        ("py-html-checker", logging.ERROR, "This is a basic exception."),
        ("py-html-checker", logging.INFO, "https://www.google.com/"),
        ("py-html-checker", logging.ERROR, "This is a basic exception.")
    ]

    runner = CliRunner()

    with runner.isolated_filesystem():
        args = ["--safe",
                os.path.join(settings.fixtures_path, "sitemap.xml")]

        result = runner.invoke(cli_frontend, ["site"] + args)

        assert result.exit_code == 0
        assert expected == caplog.record_tuples
