import os

from html_checker.utils import is_file


# Shared options arguments
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
    "safe": {
        "args": ('--safe',),
        "kwargs": {
            "is_flag": True,
            "help": (
                "Invalid paths won't break execution of script "
                "and it will be able to continue to the end."
            ),
        }
    },
    "split": {
        "args": ('--split',),
        "kwargs": {
            "is_flag": True,
            "help": (
                "Execute validation for each path in its own distinct instance. "
                "Useful for very large path list which may take too long to "
                "display anything until every path has been validated. However, "
                "for small or moderate path list it will be longer than packed "
                "execution."
            ),
        }
    },
}


def validate_paths(logger, paths):
    """
    Validate file paths.

    Invalid file path is a no critical error which should not stop program
    execution.

    NOTE: This should return a list of invalid path, not a simple counter. This
    way, invalid path could be passer to validator to ignore them.

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
                logger.error(msg.format(item))
                errors += 1
            elif os.path.isdir(item):
                msg = "Directory path are not supported: {}"
                logger.error(msg.format(item))
                errors += 1

    return errors


def validate_sitemap_path(logger, path):
    """
    Validate sitemap file path.

    Invalid sitemap file path is a critical error which should stop program
    execution.

    NOTE: Integer counter is not really accurate here since there will be
    always a single path, it should just return a boolean.

    Arguments:
        logger (logging.logger): Logging object to output error messages.
        paths (list): List of path to validate, only filepaths are checked.

    Returns:
        integer: Error counter.
    """
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
