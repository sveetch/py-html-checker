import logging
import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend
from html_checker.exceptions import HtmlCheckerBaseException
from html_checker.validator import ValidatorInterface


EXCEPTION_PATH_TRIGGER = "http://localhost/trigger-exception"


def mock_validator_execute_validator_for_base_exception(*args, **kwargs):
    """
    Raise an exception "HtmlCheckerBaseException" when a command contains
    "http://localhost/trigger-exception" (using an http url instead of a path
    ensure path validation won't occurs from reporter).
    """
    cls = args[0]
    command = args[1]

    if EXCEPTION_PATH_TRIGGER in command:
        raise HtmlCheckerBaseException("This is a dummy exception.")

    return cls.execute_validator(*args[1:], **kwargs)


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
    With safe mode disabled, internal exception should not be catched and
    will abort program execution.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator_for_base_exception)

    paths = [
        settings.format("{FIXTURES}/html/valid.basic.html"),
        EXCEPTION_PATH_TRIGGER,
    ]

    expected = []

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        # NOTE: No logs are created since we raise the exception before
        # exporter can start anything
        #expected = [
            ##("py-html-checker", logging.INFO, "http://localhost/nope"),
        #]
        #expected = [(k, l, settings.format(v)) for k,l,v in expected]

        result = runner.invoke(cli_frontend, ["page"] + paths)

        #print("=> result.exit_code <=")
        #print(result.exit_code)
        #print()
        #print("=> result.output <=")
        #print(result.output)
        #print()
        #print("=> expected <=")
        #print(expected)
        #print()
        #print("=> caplog.record_tuples <=")
        #print(caplog.record_tuples)
        #print()
        #print("=> result.exception <=")
        #print(type(result.exception))
        #print(result.exception)
        ##raise result.exception

        assert (result.exception is not None) == True
        assert isinstance(result.exception, HtmlCheckerBaseException) == True

        assert result.exit_code == 1

        assert caplog.record_tuples == expected


#@pytest.mark.skip(reason="fail until i found why after 'machin' file does not exists, validator continue to validate 'machin'.")
def test_page_safe_exception(monkeypatch, caplog, settings):
    """
    With safe mode enabled an internal exception should be catched.

    Need to be cloned for split mode.

    TODO:

    - Invalid file path is found from reporter init before validator is
      executed and just return a log instead of exception.

    - Error occured from validator does not break the validator execution
      (vnu report it but does not break on)

    So current tests can not find any exception. This was the purpose of the
    "mock_validator_execute_validator_for_base_exception". Safe mode purpose is
    to protect validator execution from exception to continue validation. Maybe
    splitted test are not relevant ?


    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator_for_base_exception)

    paths = [
        "machin",
        "http://localhost/nope",
        EXCEPTION_PATH_TRIGGER,
        settings.format("{FIXTURES}/html/valid.basic.html"),
    ]

    expected = [
        ("py-html-checker", logging.ERROR, "Given path does not exists: machin"), # This one should not be raised
        ("py-html-checker", logging.INFO, "machin"),
        ("py-html-checker", logging.ERROR, "File path does not exists."),
        ("py-html-checker", logging.ERROR, "This is a dummy exception."),
        ("py-html-checker", logging.INFO, "http://localhost/nope"),
        ("py-html-checker", logging.ERROR, "This is a dummy exception."),
        ("py-html-checker", logging.INFO, "http://localhost/trigger-exception"),
        ("py-html-checker", logging.ERROR, "This is a dummy exception."),
        ("py-html-checker", logging.INFO, settings.format("{FIXTURES}/html/valid.basic.html")),
        ("py-html-checker", logging.ERROR, "This is a dummy exception."),
    ]

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, ["page", "--safe"] + paths)

        print("=> result.output <=")
        print(result.output)
        print()
        print("=> expected <=")
        print(expected)
        print()
        print("=> caplog.record_tuples <=")
        print(caplog.record_tuples)
        print()
        print("=> result.exception <=")
        print(result.exception)
        #raise result.exception

        assert result.exit_code == 0

        assert expected == caplog.record_tuples
        #assert 1 == 33
