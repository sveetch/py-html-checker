def is_file(path):
    """
    Check if given path is a file path.

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
