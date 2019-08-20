import os

import pytest

from click.testing import CliRunner

from html_checker.cli.console_script import cli_frontend


def test_page_missing_args(caplog):
    """
    Invoked without any arguments fails because it need at least a path.
    """
    runner = CliRunner()

    # Temporary isolated current dir
    with runner.isolated_filesystem():
        test_cwd = os.getcwd()

        result = runner.invoke(cli_frontend, ['page'])

        print(result.output)

        assert result.exit_code == 2

        assert caplog.record_tuples == []
