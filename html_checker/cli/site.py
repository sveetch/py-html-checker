# -*- coding: utf-8 -*-
import json
import logging
import os

from collections import OrderedDict

import click

from html_checker.cli.common import validate_paths, validate_sitemap_path
from html_checker.report import LogExportBase
from html_checker.sitemap import Sitemap
from html_checker.utils import is_file
from html_checker.validator import ValidatorInterface


@click.command()
@click.option('--Xss', metavar="SIZE", help="Java thread stack size. Useful in some case where you encounter error 'StackOverflowError' from validator. Set it to something like '512k'.", default=None)
@click.option('--no-stream', is_flag=True, help="Forces all documents to be be parsed in buffered mode instead of streaming mode (causes some parse errors to be treated as non-fatal document errors instead of as fatal document errors).")
@click.argument('path', required=True)
@click.pass_context
def site_command(context, xss, no_stream, path):
    """
    Validate pages from given sitemap.

    Sitemap path can be an url starting with 'http://' or 'https://' or a file path.
    """
    logger = logging.getLogger("py-html-checker")

    logger.debug("Opening sitemap".format(path))

    # Validate sitemap path
    errors = validate_sitemap_path(logger, path)
    if errors > 0:
        raise click.Abort()

    # Open sitemap to get paths
    parser = Sitemap()
    paths = parser.get_urls(path)

    # Compile options
    interpreter_options = OrderedDict([])
    tool_options = OrderedDict([])

    if no_stream:
        tool_options["--no-stream"] = None

    if xss:
        key = "-Xss{}".format(xss)
        interpreter_options[key] = None

    logger.debug("Launching validation for {} paths".format(len(paths)))

    # Validate paths from sitemap
    errors = validate_paths(logger, paths)
    if errors > 0:
        raise click.Abort()

    # Get report from validator process
    v = ValidatorInterface()
    report = v.validate(paths, interpreter_options=interpreter_options,
                        tool_options=tool_options)

    #print()
    #print(json.dumps(report, indent=4))
    #print()

    # Export report
    exporter = LogExportBase()
    exporter.build(report)
