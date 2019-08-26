# -*- coding: utf-8 -*-
import json
import logging
import os

import click

from html_checker.report import LogExportBase
from html_checker.utils import is_file
from html_checker.validator import ValidatorInterface


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

    # Validate paths
    errors = 0
    for item in paths:
        if is_file(item):
            if not os.path.exists(item):
                logger.critical("Given path does not exists: {}".format(item))
                errors += 1
            elif os.path.isdir(item):
                logger.critical("Directory path are not supported: {}".format(item))
                errors += 1
    if errors > 0:
        raise click.Abort()

    # Get report from validator process
    v = ValidatorInterface()
    report = v.validate(paths)

    #print()
    #print(json.dumps(report, indent=4))
    #print()

    # Export report
    exporter = LogExportBase()
    exporter.build(report)
