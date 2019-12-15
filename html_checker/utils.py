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
