import io
import os
import subprocess

import html_checker
from html_checker.exceptions import HtmlCheckerBaseException


def is_local_ressource(path):
    """
    Check if given path is a local ressource.

    Arguments:
        path (string): Ressource path.

    Returns:
        bool: True if file path, else False.
    """
    if not path.startswith("http://") and not path.startswith("https://"):
        return True

    return False


def is_url(path):
    """
    Check if given path is an url path.

    Arguments:
        path (string): Ressource path.

    Returns:
        bool: True if url path, else False.
    """
    if path.startswith("http://") or path.startswith("https://"):
        return True

    return False


def reduce_unique(items):
    """
    Reduce given list to a list of unique values and respecting original order
    base on first value occurences.

    Arguments:
        items (list): List of element to reduce.

    Returns:
        list: List of unique values.
    """
    used = set()
    return [x for x in items if x not in used and (used.add(x) or True)]


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


def get_application_path():
    """
    Return path to Py Html Checker module.

    Returns:
        string: Absolute path to application module.
    """
    return os.path.abspath(
        os.path.dirname(html_checker.__file__)
    )


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


def merge_compute(left, right):
    """
    Merge two dictionnaries but computing integer values instead of overriding.

    Left override every right values except when both left and right value are
    integers then right value will be incremented by left value.

    Arguments:
        left (dict): The dict to merge into right.
        right (dict): The merge in the left dict.

    Returns:
        dict: Merged dict from left to right.
    """
    for k, v in left.items():
        # Only compute item if both left and right values are integers, else
        # left override right value
        if k in right and type(v) is int and type(right[k]) is int:
            right[k] += v
        else:
            right[k] = v

    return right


def resolve_paths(*paths):
    """
    A shortand to join paths and resolve their combination to full absolute
    path.

    * Path normalization (for ``.`` and ``..``) is applied;
    * ``~`` is resolved to user home directory;
    * Path is turned to absolute path if not already done;

    Arguments:
        *args (list): Paths to combine and resolve into an absolute and
            normalized path.

    Returns:
        string: Absolute path.
    """
    return os.path.abspath(
        os.path.expanduser(
            os.path.normpath(
                os.path.join(*paths)
            )
        )
    )


def write_documents(destination, documents):
    """
    Write every given documents files into destination directory.

    Arguments:
        destination (string): Destination directory where to write files. If
            given directory path does not exist, it will be created.
        documents (list): List of document datas with item ``document`` for
            document filepath where to write and item ``content`` for content
            string to write to file.

    Returns:
        list: List of writed documents
    """
    files = []

    if not os.path.exists(destination):
        os.makedirs(destination)

    for doc in documents:
        file_destination = resolve_paths(destination, doc["document"])
        files.append(file_destination)

        with io.open(file_destination, 'w') as fp:
            fp.write(doc["content"])

    return files
