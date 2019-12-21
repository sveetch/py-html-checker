import pytest

from click.testing import CliRunner

from html_checker.cli.entrypoint import cli_frontend


def test_version_ping(caplog):
    """
    Just ping version command, should always be successful without any logs.
    """
    runner = CliRunner()

    result = runner.invoke(cli_frontend, ['version'])

    assert result.exit_code == 0

    assert caplog.record_tuples == []
