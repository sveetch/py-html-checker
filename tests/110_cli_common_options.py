"""
These tests cover shared options for page and site command. They mockup some
validator, exporter and sitemap method to just return command line without
processing or executing anything else.
"""
import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend
from html_checker.export import LogExportBase
from html_checker.validator import ValidatorInterface
from html_checker.sitemap import Sitemap


class DummyReport:
    """
    A dummy reporter to simulate ReportStore signatures but just to add
    given paths in registry
    """
    def __init__(self, *args, **kwargs):
        self.registry = []

    def add(self, content):
        self.registry.extend(content)


def mock_validator_execute_validator(*args, **kwargs):
    """
    Mock method to just return the builded command line without
    executing it.
    """
    cls = args[0]
    command = args[1]
    return command


def mock_export_build(*args, **kwargs):
    """
    Mock method to just print out the given command line in ``report``
    argument (following validator mockups).
    """
    cls = args[0]
    report = args[1]
    cls.log.info(" ".join(report.registry))


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
    monkeypatch.setattr(ValidatorInterface, "REPORT_CLASS", DummyReport)
    monkeypatch.setattr(LogExportBase, "build", mock_export_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = (
        "java"
        " -Xss512k"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
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
    monkeypatch.setattr(ValidatorInterface, "REPORT_CLASS", DummyReport)
    monkeypatch.setattr(LogExportBase, "build", mock_export_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = (
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --no-stream"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
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

        assert result.exit_code == 0
        assert expected == caplog.record_tuples


@pytest.mark.parametrize("command_name", [
    "page",
    "site",
])
def test_user_agent(monkeypatch, caplog, settings, command_name):
    """
    '--user-agent' option should be correctly added to every part.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator)
    monkeypatch.setattr(ValidatorInterface, "REPORT_CLASS", DummyReport)
    monkeypatch.setattr(LogExportBase, "build", mock_export_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = (
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --user-agent Foobar"
        " --format json"
        " --exit-zero-always"
        " http://perdu.com"
    )
    expected = [
        ("py-html-checker", 20, settings.format(commandline)),
    ]

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, [
            command_name, "--user-agent", "Foobar", "http://perdu.com"
        ])

        assert result.exit_code == 0
        assert expected == caplog.record_tuples


@pytest.mark.parametrize("split,expected_paths", [
    (False, ["http://foo.com http://bar.com"]),
    (True, ["http://foo.com", "http://bar.com"]),
])
def test_page_split(monkeypatch, caplog, settings, split, expected_paths):
    """
    '--split' option should cause executing a new validator instance on each
    path and only one for all path when not enabled.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator)
    monkeypatch.setattr(ValidatorInterface, "REPORT_CLASS", DummyReport)
    monkeypatch.setattr(LogExportBase, "build", mock_export_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = (
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
        " "
    )

    # Build expected logs
    expected = []
    for p in expected_paths:
        expected.append(
            ("py-html-checker", 20, settings.format(commandline) + p)
        ),

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["page"]
        if split:
            args.append("--split")
        args.append("http://foo.com")
        args.append("http://bar.com")

        result = runner.invoke(cli_frontend, args)

        assert result.exit_code == 0
        assert expected == caplog.record_tuples


@pytest.mark.parametrize("split,expected_paths", [
    (False, ["http://foo.com http://bar.com"]),
    (True, ["http://foo.com", "http://bar.com"]),
])
def test_site_split(monkeypatch, caplog, settings, split, expected_paths):
    """
    '--split' option should cause executing a new validator instance on each
    path and only one for all path when not enabled.
    """
    def mock_sitemap_get_urls(*args, **kwargs):
        """
        Mock method to just return harcoded paths we expect from parsed sitemap
        """
        return ["http://foo.com", "http://bar.com"]

    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator)
    monkeypatch.setattr(ValidatorInterface, "REPORT_CLASS", DummyReport)
    monkeypatch.setattr(LogExportBase, "build", mock_export_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = (
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
        " "
    )

    # Build expected logs
    expected = []
    for p in expected_paths:
        expected.append(
            ("py-html-checker", 20, settings.format(commandline) + p)
        ),

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        args = ["site"]
        if split:
            args.append("--split")
        args.append("http://perdu.com/sitemap.xml")

        result = runner.invoke(cli_frontend, args, catch_exceptions=False)

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
        assert expected == caplog.record_tuples
