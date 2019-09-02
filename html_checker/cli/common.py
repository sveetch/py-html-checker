import os

from html_checker.utils import is_file


def validate_paths(logger, paths):
    """
    Validate file paths.

    Arguments:
        logger (logging.logger): Logging object to output error messages.
        paths (list): List of path to validate, only filepaths are checked.

    Returns:
        integer: Error counter.
    """
    errors = 0

    for item in paths:
        if is_file(item):
            if not os.path.exists(item):
                msg = "Given path does not exists: {}"
                logger.critical(msg.format(item))
                errors += 1
            elif os.path.isdir(item):
                msg = "Directory path are not supported: {}"
                logger.critical(msg.format(item))
                errors += 1

    return errors



def validate_sitemap_path(logger, path):
    errors = 0

    if is_file(path):
        if not os.path.exists(path):
            msg = "Given sitemap path does not exists: {}"
            logger.critical(msg.format(path))
            errors += 1
        elif os.path.isdir(path):
            msg = "Directory sitemap path are not supported: {}"
            logger.critical(msg.format(path))
            errors += 1

    return errors
