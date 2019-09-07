import os

from html_checker.utils import is_file


# Shared options
COMMON_OPTIONS = {
    "xss": {
        "args": ('--Xss',),
        "kwargs": {
            "metavar": "SIZE",
            "help": (
                "Java thread stack size. Useful in some case where you "
                "encounter error 'StackOverflowError' from validator. Set it "
                "to something like '512k'."
            ),
            "default": None,
        }
    },
    "no-stream": {
        "args": ('--no-stream',),
        "kwargs": {
            "is_flag": True,
            "help": (
                "Forces all documents to be be parsed in buffered mode instead "
                "of streaming mode (causes some parse errors to be treated as "
                "non-fatal document errors instead of as fatal document errors)."
            ),
        }
    },
    "user-agent": {
        "args": ('--user-agent',),
        "kwargs": {
            "metavar": "STRING",
            "help": (
                "A customer user-agent to use for every possible requests."
            ),
        }
    },
}


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