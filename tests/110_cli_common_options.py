import logging
import os

import pytest

from click.testing import CliRunner

import cherrypy

from html_checker.cli.entrypoint import cli_frontend
from html_checker.export import LoggingExport
from html_checker.validator import ValidatorInterface
from html_checker.serve import ReleaseServer
from html_checker.sitemap import Sitemap


class DummyReport:
    """
    A dummy reporter to simulate ReportStore signatures but just to add
    given paths in registry
    """
    def __init__(self, *args, **kwargs):
        self.registry = []

    def add(self, content):
        self.registry.append(content)


def mock_cherrypy_quickstart(*args, **kwargs):
    """
    Mock quickstart to do nothing.
    """
    pass


def mock_validator_execute_validator(*args, **kwargs):
    """
    Mock method to just return the built command line without
    executing it.
    """
    command = args[1]
    return command


def mock_export_logging_build(*args, **kwargs):
    """
    Mock method to only logs given command lines in ``report``
    argument (following validator mockups) without doing any build.
    """
    cls = args[0]
    report = args[1]
    for k in report:
        cls.log.info(" ".join(k))


def mock_sitemap_get_urls(*args, **kwargs):
    """
    Mock method to just return given url as argument so it can pass the dummy
    url to validator without to read it like a sitemap.
    """
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
    monkeypatch.setattr(LoggingExport, "build", mock_export_logging_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    sample = settings.fixtures_path / "html/valid.basic.html"

    commandline = (
        "java"
        " -Xss512k"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
        " {source}"
    )
    extra = {"source": sample}

    expected = []
    if command_name == "site":
        expected.append(
            ("py-html-checker", logging.INFO, "Sitemap have 1 paths"),
        )
    else:
        expected.append(
            ("py-html-checker", logging.INFO, "Launching validation for 1 paths"),
        )

    expected.append(
        ("py-html-checker", logging.INFO, settings.format(commandline, extra=extra)),
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli_frontend, [
            command_name, "--Xss", "512k", str(sample)
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
    monkeypatch.setattr(LoggingExport, "build", mock_export_logging_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    sample = settings.fixtures_path / "html/valid.basic.html"

    commandline = (
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --no-stream"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
        " {source}"
    )
    extra = {"source": sample}

    expected = []
    if command_name == "site":
        expected.append(
            ("py-html-checker", logging.INFO, "Sitemap have 1 paths"),
        )
    else:
        expected.append(
            ("py-html-checker", logging.INFO, "Launching validation for 1 paths"),
        )

    expected.append(
        ("py-html-checker", logging.INFO, settings.format(commandline, extra=extra)),
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli_frontend, [
            command_name, "--no-stream", str(sample)
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
    monkeypatch.setattr(LoggingExport, "build", mock_export_logging_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    sample = settings.fixtures_path / "html/valid.basic.html"

    commandline = (
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --user-agent Foobar"
        " --format json"
        " --exit-zero-always"
        " {source}"
    )
    extra = {"source": sample}

    expected = []
    if command_name == "site":
        expected.append(
            ("py-html-checker", logging.INFO, "Sitemap have 1 paths"),
        )
    else:
        expected.append(
            ("py-html-checker", logging.INFO, "Launching validation for 1 paths"),
        )

    expected.append(
        ("py-html-checker", logging.INFO, settings.format(commandline, extra=extra)),
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli_frontend, [
            command_name, "--user-agent", "Foobar", str(sample)
        ])

        assert result.exit_code == 0
        assert expected == caplog.record_tuples


@pytest.mark.parametrize("command_name", [
    "page",
    # "site",
])
def test_serve(monkeypatch, caplog, tmp_path, settings, command_name):
    """
    Once enabled the option '--server' should build report in a given destination
    directory then serve.
    """
    monkeypatch.setattr(cherrypy, "quickstart", mock_cherrypy_quickstart)

    sample = settings.fixtures_path / "html/valid.basic.html"

    if command_name == "site":
        command_type_specific_log = "Sitemap have 1 paths"
    else:
        command_type_specific_log = "Launching validation for 1 paths"

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        cli = [
            command_name,
            "--exporter", "html",
            "--serve", "0.0.0.0:8080",
            "--destination", test_cwd,
            str(sample)
        ]

        result = runner.invoke(cli_frontend, cli)

        assert result.exit_code == 0
        assert caplog.record_tuples == [
            ("py-html-checker", logging.INFO, command_type_specific_log),
            ("py-html-checker", 20, str(sample)),
            ("py-html-checker", 20, "Created file: {}/index.html".format(test_cwd)),
            ("py-html-checker", 20, "Created file: {}/main.css".format(test_cwd)),
            ("py-html-checker", 20, "Starting HTTP server on: 0.0.0.0:8080"),
            ("py-html-checker", 30, "Use CTRL+C to terminate.")
        ]


@pytest.mark.parametrize("command_name", [
    "page",
    # "site",
])
def test_serve_on_temporary(monkeypatch, caplog, tmp_path, settings, command_name):
    """
    Once enabled the option '--server' should build report in a temporary directory
    then serve.
    """
    # Mocked up 'mkdtemp' method will just returns the current 'tmp_path' value so we
    # have a stable value to assert on
    def mock_releaseserver_mkdtemp(*args, **kwargs):
        return tmp_path

    monkeypatch.setattr(ReleaseServer, "mkdtemp", mock_releaseserver_mkdtemp)
    monkeypatch.setattr(cherrypy, "quickstart", mock_cherrypy_quickstart)

    sample = settings.fixtures_path / "html/valid.basic.html"

    if command_name == "site":
        command_type_specific_log = "Sitemap have 1 paths"
    else:
        command_type_specific_log = "Launching validation for 1 paths"

    runner = CliRunner()
    with runner.isolated_filesystem():
        cli = [
            command_name,
            "--exporter", "html",
            "--serve", "0.0.0.0:8080",
            str(sample)
        ]

        result = runner.invoke(cli_frontend, cli)

        assert result.exit_code == 0

        assert caplog.record_tuples == [
            ("py-html-checker", logging.INFO, command_type_specific_log),
            ("py-html-checker", 20, str(sample)),
            ("py-html-checker", 20, "Created file: {}/index.html".format(tmp_path)),
            ("py-html-checker", 20, "Created file: {}/main.css".format(tmp_path)),
            ("py-html-checker", 20, "Starting HTTP server on: 0.0.0.0:8080"),
            ("py-html-checker", 30, "Use CTRL+C to terminate.")
        ]

        # On command exit the temporary directory has been removed
        assert tmp_path.exists() is False


@pytest.mark.parametrize("split, paths", [
    (
        False,
        ["http://foo.com", "http://bar.com"],
    ),
    (
        True,
        ["http://foo.com", "http://bar.com"],
    ),
])
def test_page_split(monkeypatch, caplog, settings, split, paths):
    """
    '--split' option should cause executing a new nvu validator instance on
    each path and only one for all path when not enabled.
    """
    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator)
    monkeypatch.setattr(ValidatorInterface, "REPORT_CLASS", DummyReport)
    monkeypatch.setattr(LoggingExport, "build", mock_export_logging_build)

    commandline = settings.format((
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
        " "
    ))

    # Build expected logs depending split option
    initial_msg = "Launching validation for {} paths"
    expected = [
        ("py-html-checker", logging.INFO, initial_msg.format(len(paths))),
    ]

    # In split mode, there should one command line for each path
    if split:
        for p in paths:
            log = ("py-html-checker", logging.INFO, commandline + p)
            expected.append(
                log
            ),
    # Else there should be only one command line for all paths
    else:
        expected.append(
            ("py-html-checker", logging.INFO, commandline + " ".join(paths))
        ),

    runner = CliRunner()
    with runner.isolated_filesystem():
        args = ["page"]
        if split:
            args.append("--split")
        for item in paths:
            args.append(item)

        result = runner.invoke(cli_frontend, args)

        assert result.exit_code == 0
        assert expected == caplog.record_tuples


@pytest.mark.parametrize("split, paths", [
    (
        False,
        ["http://foo.com", "http://bar.com"],
    ),
    (
        True,
        ["http://foo.com", "http://bar.com"],
    ),
])
def test_site_split(monkeypatch, caplog, settings, split, paths):
    """
    '--split' option should cause executing a new vnu validator instance on
    each path and only one for all path when option is disabled.
    """
    def mock_sitemap_get_urls(*args, **kwargs):
        """
        Mock method to just return harcoded dummy paths we expect from parsed
        sitemap
        """
        return ["http://foo.com", "http://bar.com"]

    monkeypatch.setattr(ValidatorInterface, "execute_validator",
                        mock_validator_execute_validator)
    monkeypatch.setattr(ValidatorInterface, "REPORT_CLASS", DummyReport)
    monkeypatch.setattr(LoggingExport, "build", mock_export_logging_build)
    monkeypatch.setattr(Sitemap, "get_urls", mock_sitemap_get_urls)

    commandline = settings.format((
        "java"
        " -jar {APPLICATION}/vnujar/vnu.jar"
        " --format json"
        " --exit-zero-always"
        " --user-agent {USER_AGENT}"
        " "
    ))

    # Build expected logs
    initial_msg = "Sitemap have {} paths"
    expected = [
        ("py-html-checker", logging.INFO, initial_msg.format(len(paths))),
    ]

    # In split mode, there should be one command line for each path
    if split:
        for p in paths:
            log = ("py-html-checker", logging.INFO, commandline + p)
            expected.append(
                log
            ),
    # Else there should be only a single command line for all paths
    else:
        expected.append(
            ("py-html-checker", logging.INFO, commandline + " ".join(paths))
        ),

    runner = CliRunner()
    with runner.isolated_filesystem():
        args = ["site"]
        if split:
            args.append("--split")
        args.append("http://perdu.com/sitemap.xml")

        result = runner.invoke(cli_frontend, args, catch_exceptions=False)

        assert result.exit_code == 0
        assert expected == caplog.record_tuples
