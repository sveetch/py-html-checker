# -*- coding: utf-8 -*-
import json
import logging
import os

import click

from html_checker.report import LogExportBase
from html_checker.sitemap import Sitemap
from html_checker.utils import is_file
from html_checker.validator import ValidatorInterface


@click.command()
@click.argument('path', required=True)
@click.pass_context
def site_command(context, path):
    """
    Validate pages from given sitemap.

    Sitemap path can be an url starting with 'http://' or 'https://' or a file path.
    """
    logger = logging.getLogger("py-html-checker")

    logger.debug("Opening sitemap".format(path))

    # Validate sitemap path
    errors = 0
    if is_file(path):
        if not os.path.exists(path):
            logger.critical("Given sitemap path does not exists: {}".format(path))
            errors += 1
        elif os.path.isdir(path):
            logger.critical("Directory sitemap path are not supported: {}".format(path))
            errors += 1
    if errors > 0:
        raise click.Abort()

    # Open sitemap to get paths
    parser = Sitemap()
    paths = parser.get_urls(path)

    logger.debug("Launching validation for given {} paths".format(len(paths)))

    # Validate paths from sitemap
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
