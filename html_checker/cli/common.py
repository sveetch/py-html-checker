import os

import click

from html_checker.utils import is_local_ressource

from html_checker.export import EXPORTER_CHOICES


# Shared options arguments
COMMON_OPTIONS = {
    "destination": {
        "args": ("--destination",),
        "type": click.Path(),
        "kwargs": {
            "metavar": "FILEPATH",
            "help": (
                "Directory path where to write report files. If destination "
                "is not given, every files will be printed out. You can use a "
                "dot to write files to your current directory, a relative "
                "path or an absolute path. Path can start with '~' to point "
                "to your user home directory."
            ),
            "default": None,
        }
    },
    "pack": {
        "args": ("--pack/--no-pack",),
        "kwargs": {
            "default": True,
            "help": (
                "Pack reports into a single file or not. Default is to pack "
                "everything in a single file. 'no-pack' will create a file "
                "for each report and then an export summary."
                "It is recommended to define a destination directory with "
                "'--destination' if you don't plan to use packed export, else "
                "every files will just be printed out in an unique output. "
                "This option has no effect with ``logging`` format."
            ),
        }
    },
    "exporter": {
        "args": ("--exporter",),
        "kwargs": {
            "type": click.Choice(EXPORTER_CHOICES, case_sensitive=False),
            "help": (
                "Select exporter format."
            ),
            "default": "logging",
        }
    },
    "no-stream": {
        "args": ("--no-stream",),
        "kwargs": {
            "is_flag": True,
            "help": (
                "Forces all documents to be be parsed in buffered mode instead "
                "of streaming mode (causes some parse errors to be treated as "
                "non-fatal document errors instead of as fatal document errors)."
            ),
        }
    },
    "safe": {
        "args": ("--safe",),
        "kwargs": {
            "is_flag": True,
            "help": (
                "Invalid paths won't break execution of script "
                "and it will be able to continue to the end. This is mostly "
                "for rare usecase when invalid source encounter a bug from "
                "report parsing or from validator."
            ),
        }
    },
    "source": {
        "args": ("--source/--no-source",),
        "kwargs": {
            "default": True,
            "help": (
                "Include full HTML source in report for each path. You can "
                "disable it when you have too many paths with too much big "
                "sources. NOT IMPLEMENTED YET."
            ),
        }
    },
    "split": {
        "args": ("--split",),
        "kwargs": {
            "is_flag": True,
            "help": (
                "Execute validation for each path in its own distinct instance. "
                "Useful for very large path list which may take too long to "
                "display anything until every path has been validated. However, "
                "for small or moderate path list it will be longer than unique "
                "instance."
            ),
        }
    },
    "template-dir": {
        "args": ("--template-dir",),
        "type": click.Path(exists=True, file_okay=False, dir_okay=True),
        "kwargs": {
            "metavar": "PATH",
            "help": (
                "A path to a template directory for your custom templates. "
                "Your template directory must contains the summary, report "
                "and audit main templates and also a 'main.css' file. This "
                "option has only effect for 'html' exporter."
            ),
        }
    },
    "user-agent": {
        "args": ("--user-agent",),
        "kwargs": {
            "metavar": "STRING",
            "help": (
                "A customer user-agent to use for every possible requests."
            ),
        }
    },
    "xss": {
        "args": ("--Xss",),
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
}


def validate_sitemap_path(logger, path):
    """
    Validate sitemap file path.

    Invalid sitemap file path is a critical error which should stop program
    execution.

    Arguments:
        logger (logging.logger): Logging object to output error messages.
        paths (list): List of path to validate, only filepaths are checked.

    Returns:
        bool: ``True`` if given filepath is a valid local path or an url, else
        it returns ``False``.
    """
    if is_local_ressource(path):
        if not os.path.exists(path):
            msg = "Given sitemap path does not exists: {}".format(path)
            logger.critical(msg)
            return False
        elif os.path.isdir(path):
            msg = "Directory sitemap path are not supported: {}".format(path)
            logger.critical(msg)
            return False

    return True
