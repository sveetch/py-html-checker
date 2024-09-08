import os

import html_checker


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


def get_application_path():
    """
    Return path to Py Html Checker module.

    Returns:
        string: Absolute path to application module.
    """
    return os.path.abspath(
        os.path.dirname(html_checker.__file__)
    )


def resolve_paths(*paths):
    """
    A shortand to join paths and resolve their combination to full absolute
    path.

    * Path normalization (for ``.`` and ``..``) is applied;
    * ``~`` is resolved to user home directory;
    * Path is turned to absolute path if not already done;

    .. Note::
        This helper would be almost useless if we used ``pathlib`` instead of ``os``.

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
