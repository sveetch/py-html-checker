"""
These tests cover shared options for page and site command. They mockup some
validator, exporter and sitemap method to just return command line without
processing or executing anything else.
"""
import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend
from html_checker.report import LogExportBase
from html_checker.validator import ValidatorInterface
from html_checker.sitemap import Sitemap


def mock_validator_execute_validator(*args, **kwargs):
    """
    Mock method to just return the builded command line without
    executing it.
    """
    cls = args[0]
    command = args[1]
    return command


def mock_validator_parse_report(*args, **kwargs):
    """
    Mock method to just return the returned command line from
    ``execute_validator``.
    """
    cls = args[0]
    paths = args[1]
    process = args[2]
    return process


def mock_export_build(*args, **kwargs):
    """
    Mock method to just print out the given command line in ``report``
    argument (following validator mockups).
    """
    cls = args[0]
    report = args[1]
    cls.log.info(" ".join(report))


def mock_sitemap_get_urls(*args, **kwargs):
    """
    Mock method to just return given url as argument so it can pass the dummy
    url to validator without to read it like a sitemap
    """
    cls = args[0]
    path = args[1]
    return [path]


@pytest.mark.parametrize("command_name", [
    "page",
    "site",
])
def test_interpreter_xss(monkeypatch, caplog, settings, command_name):
    """
    '-Xss' option should be correctly added to interpreter part.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator)
    monkeypatch.setattr(ValidatorInterface, "parse_report", mock_validator_parse_report)
    monkeypatch.setattr(LogExportBase, "build", mock_export_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = (
        "java"
        " -Xss512k"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --format json"
        " --exit-zero-always"
        " --user-agent Validator.nu/LV py-html-checker/0.1.0"
        " http://perdu.com"
    )
    expected = [
        ("py-html-checker", 20, settings.format(commandline)),
    ]

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, [
            command_name, "--Xss", "512k", "http://perdu.com"
        ])

        print(result.output)
        print(result.exception)
        print(caplog.record_tuples)

        assert result.exit_code == 0
        assert expected == caplog.record_tuples


@pytest.mark.parametrize("command_name", [
    "page",
    "site",
])
def test_interpreter_nostream(monkeypatch, caplog, settings, command_name):
    """
    '--no-stream' option should be correctly added to interpreter part.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator)
    monkeypatch.setattr(ValidatorInterface, "parse_report", mock_validator_parse_report)
    monkeypatch.setattr(LogExportBase, "build", mock_export_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = (
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --no-stream"
        " --format json"
        " --exit-zero-always"
        " --user-agent Validator.nu/LV py-html-checker/0.1.0"
        " http://perdu.com"
    )
    expected = [
        ("py-html-checker", 20, settings.format(commandline)),
    ]

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, [
            command_name, "--no-stream", "http://perdu.com"
        ])

        print(result.output)
        print(result.exception)
        print()
        print(expected)
        print(caplog.record_tuples)

        assert result.exit_code == 0
        assert expected == caplog.record_tuples
