import logging
import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend
from html_checker.exceptions import HtmlCheckerBaseException
from html_checker.validator import ValidatorInterface


def mock_validator_execute_validator_for_base_exception(*args, **kwargs):
    """
    Always raise an exception "HtmlCheckerBaseException" to exception catching
    """
    raise HtmlCheckerBaseException("This is a basic exception.")


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
            ("py-html-checker", logging.ERROR, "Given path does not exists: foo.html"),
            ("py-html-checker", logging.ERROR, "Given path does not exists: bar.html"),
            ("py-html-checker", logging.ERROR, "Directory path are not supported: {FIXTURES}/html/")
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
            ("py-html-checker", logging.ERROR, "Given path does not exists: foo.html"),
            ("py-html-checker", logging.ERROR, "Given path does not exists: bar.html"),
            ("py-html-checker", logging.ERROR, "Directory path are not supported: {FIXTURES}/html/"),
            # These ones should be removed further when validator+export workflow
            # is refactored to ignore invalid files
            ("py-html-checker", logging.ERROR, "File path does not exists."),
            ("py-html-checker", logging.ERROR, "File path does not exists."),
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        # Lower logger to ERROR only, this test doesnt need to check everything
        result = runner.invoke(cli_frontend, ["-v", "2", "page"] + args)

        print("=> result.exit_code <=")
        print(result.exit_code)
        print()
        print("=> result.output <=")
        print(result.output)
        print()
        print("=> result.exception <=")
        print(result.exception)
        print()
        print("=> expected <=")
        print(expected)
        print()
        print("=> caplog.record_tuples <=")
        print(caplog.record_tuples)

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


def test_page_nosafe_exception(monkeypatch, caplog, settings):
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
        test_cwd = os.getcwd()

        expected = [
            # NOTE: Currently there cant be any log entry since we raise the
            # exception before exporter can start anything
            #("py-html-checker", logging.INFO, "http://localhost/nope"),
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        result = runner.invoke(cli_frontend, ["page", "http://localhost/nope"])

        assert isinstance(result.exception, HtmlCheckerBaseException) == True

        assert result.exit_code == 1

        assert caplog.record_tuples == expected


@pytest.mark.skip(reason="expected to fail until cli, validator and exporter have been refactored for cleaner split/path management.")
def test_page_safe_exception(monkeypatch, caplog, settings):
    """
    With safe mode enabled an internal exception should be catched.

    Use a mockup to force validator.execute_validator() method to raise a basic
    internal exception.

    TODO: Finish (see cli.page)

    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator_for_base_exception)

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, ["page", "--safe", "http://localhost/nope"])

        expected = [
            ("py-html-checker", logging.INFO, "http://localhost/nope"),
            ("py-html-checker", logging.ERROR, "This is a basic exception."),
        ]

        print("=> result.output <=")
        print(result.output)
        print()
        print("=> result.exception <=")
        print(type(result.exception))
        print(result.exception)
        print()
        print("=> caplog.record_tuples <=")
        print(caplog.record_tuples)

        assert result.exit_code == 0

        assert expected == caplog.record_tuples
