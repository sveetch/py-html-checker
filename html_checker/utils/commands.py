import subprocess

import html_checker
from ..exceptions import HtmlCheckerBaseException
from .paths import get_application_path


def execute_command(command):
    """
    Execute a process for given command.

    Arguments:
        command (list): List of command elements.

    Raises:
        HtmlCheckerBaseException: If subprocess encounter any error kind.

    Returns:
        subprocess.CompletedProcess: Process output.
    """
    try:
        process = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except FileNotFoundError as e:
        msg = "Unable to reach interpreter to run validator: {}"
        raise HtmlCheckerBaseException(msg.format(e))
    except subprocess.CalledProcessError as e:
        msg = "Validator execution failed: {}"
        raise HtmlCheckerBaseException(msg.format(e.output.decode("utf-8")))

    return process


def get_vnu_version():
    """
    Return the included validator "Nu Html Checker" version.

    Returns:
        string: Returned version string from validator execution with
        ``--version`` argument.
    """
    try:
        response = execute_command([
            html_checker.DEFAULT_INTERPRETER,
            "-jar",
            html_checker.DEFAULT_VALIDATOR.format(
                HTML_CHECKER=get_application_path()
            ),
            "--version",
        ])
    except HtmlCheckerBaseException as e:
        raise e
    else:
        return response.decode("utf-8").strip()
