# -*- coding: utf-8 -*-
import json
import logging

import click

from html_checker.validator import ValidatorInterface
from html_checker.report import LogExportBase
from html_checker.exceptions import (PathInvalidError, SitemapInvalidError,
                              ValidatorError)


@click.command()
@click.argument('paths', nargs=-1, required=True)
@click.pass_context
def page_command(context, paths):
    """
    Validate pages from given paths.

    Path can be an url starting with 'http://' or 'https://' or a file path.

    You can give many paths to validate each one.
    """
    logger = logging.getLogger("py-html-checker")

    logger.debug("Launching validation for given {} paths".format(len(paths)))

    # TODO: Validate path because we dont support directory path

    v = ValidatorInterface()
    reporter = LogExportBase()

    report = v.validate(
        paths,
    )

    print()
    print(json.dumps(report, indent=4))
    print()

    reporter.build(report)
