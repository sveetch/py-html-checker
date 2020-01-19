import io
import json
import logging
import os

import pytest

from click.testing import CliRunner

from html_checker.cli.entrypoint import cli_frontend
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
    Invalid local file paths does not abort program
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
        ]
        expected = [(k, l, settings.format(v)) for k,l,v in expected]

        # Lower logger to ERROR only, this test doesnt need to check everything
        result = runner.invoke(cli_frontend, ["-v", "2", "page"] + args)

        #print("=> result.exit_code <=")
        #print(result.exit_code)
        #print()
        #print("=> result.output <=")
        #print(result.output)
        #print()
        #print("=> result.exception <=")
        #print(result.exception)
        #print()
        #print("=> expected <=")
        #print(expected)
        #print()
        #print("=> caplog.record_tuples <=")
        #print(caplog.record_tuples)

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
            ("py-html-checker", logging.INFO, "Launching validation for 1 paths"),
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

    Also there is no expected log since we are not in split mode and mockup
    for "execute_validator" raise dummy exception with a "if X in Y".
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator_for_base_exception)

    paths = [
        settings.format("{FIXTURES}/html/valid.basic.html"),
        EXCEPTION_PATH_TRIGGER,
    ]

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, ["page"] + paths)

        #print("=> result.exit_code <=")
        #print(result.exit_code)
        #print()
        #print("=> result.output <=")
        #print(result.output)
        #print()
        #print("=> caplog.record_tuples <=")
        #print(caplog.record_tuples)
        #print()
        #print("=> result.exception <=")
        #print(type(result.exception))
        #print(result.exception)
        #if result.exception is not None:
            #raise result.exception

        assert (result.exception is not None) == True
        assert isinstance(result.exception, HtmlCheckerBaseException) == True

        assert result.exit_code == 1

        assert caplog.record_tuples == [
            ("py-html-checker",
             logging.INFO,
             "Launching validation for {} paths".format(len(paths))),
        ]


def test_page_safe_exception(monkeypatch, caplog, settings):
    """
    With safe mode enabled an internal exception should be catched.
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
        ("py-html-checker", logging.INFO, "Launching validation for {} paths".format(len(paths))),
        ("py-html-checker", logging.INFO, "machin"),
        ("py-html-checker", logging.ERROR, "Given path does not exists: machin"),
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
        #if result.exception:
            #raise result.exception

        assert result.exit_code == 0

        assert expected == caplog.record_tuples
        #assert 1 == 33


def test_page_json_destination(monkeypatch, caplog, settings):
    """
    When '--destination' is given, report files should be written into
    destination directory.

    This stands on JSON export and default pack option which produce a single
    JSON document.
    """
    paths = [
        settings.format("{FIXTURES}/html/valid.basic.html"),
    ]

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()
        dest_dir = os.path.join(test_cwd, "foop")
        expected_document = os.path.join(dest_dir, "audit.json")

        expected = [
            ("py-html-checker", logging.INFO, "Launching validation for {} paths".format(len(paths))),
            ("py-html-checker", logging.INFO, settings.format("{FIXTURES}/html/valid.basic.html")),
            ("py-html-checker", logging.INFO, "Created file: {}".format(expected_document)),
        ]

        result = runner.invoke(cli_frontend, [
            "page",
            "--exporter", "json",
            "--destination", dest_dir
        ] + paths)

        with io.open(expected_document, 'r') as fp:
            content = fp.read()

        # Ensure this is a valid JSON file as it should be
        json.loads(content)

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
        #print(result.exception)
        #if result.exception:
            #raise result.exception

        assert result.exit_code == 0

        assert expected == caplog.record_tuples
