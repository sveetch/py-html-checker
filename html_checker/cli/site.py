# -*- coding: utf-8 -*-
import logging

from collections import OrderedDict

import click

from html_checker.cli.common import (COMMON_OPTIONS, validate_paths,
                                     validate_sitemap_path)
from html_checker.exceptions import (HtmlCheckerUnexpectedException,
                                     HtmlCheckerBaseException)
from html_checker.export import LogExportBase
from html_checker.sitemap import Sitemap
from html_checker.validator import ValidatorInterface


@click.command()
@click.option(*COMMON_OPTIONS["xss"]["args"],
              **COMMON_OPTIONS["xss"]["kwargs"])
@click.option(*COMMON_OPTIONS["no-stream"]["args"],
              **COMMON_OPTIONS["no-stream"]["kwargs"])
@click.option(*COMMON_OPTIONS["user-agent"]["args"],
              **COMMON_OPTIONS["user-agent"]["kwargs"])
@click.option(*COMMON_OPTIONS["safe"]["args"],
              **COMMON_OPTIONS["safe"]["kwargs"])
@click.option(*COMMON_OPTIONS["split"]["args"],
              **COMMON_OPTIONS["split"]["kwargs"])
@click.option('--dry-run', is_flag=True,
              help=("Download and parse given Sitemap ressource and output "
                    "informations but never try to valide its items."))
@click.argument('path', required=True)
@click.pass_context
def site_command(context, xss, no_stream, user_agent, safe, split, path,
                 dry_run):
    """
    Validate pages from given sitemap.

    Sitemap path can be an url starting with 'http://' or 'https://' or a
    file path.

    Note than invalid sitemap path still raise error even with '--safe' option
    is enabled.
    """
    logger = logging.getLogger("py-html-checker")

    logger.debug("Opening sitemap".format(path))

    # Safe mode enabled, catch all internal exceptions
    if safe:
        CatchedException = HtmlCheckerBaseException
    # Safe mode disabled, watch for a dummy exception that won't never occurs
    # so internal exception are still raised
    else:
        CatchedException = HtmlCheckerUnexpectedException

    # Validate sitemap path
    errors = validate_sitemap_path(logger, path)
    if errors > 0:
        raise click.Abort()

    # Compile options
    sitemap_options = {}
    interpreter_options = OrderedDict([])
    tool_options = OrderedDict([])

    if no_stream:
        tool_options["--no-stream"] = None

    if user_agent:
        sitemap_options["user_agent"] = user_agent
        tool_options["--user-agent"] = user_agent

    if xss:
        key = "-Xss{}".format(xss)
        interpreter_options[key] = None

    # Open sitemap to get paths
    try:
        parser = Sitemap(**sitemap_options)
        paths = parser.get_urls(path)
    except CatchedException as e:
        logger.critical(e)
        raise click.Abort()

    logger.debug("Sitemap have {} paths".format(len(paths)))

    # Validate paths from sitemap
    errors = validate_paths(logger, paths)
    if not safe and errors > 0:
        raise click.Abort()

    # TODO: dry run mode does not have any test coverage yet
    if not dry_run:
        logger.debug("Launching validation for sitemap items")

        v = ValidatorInterface()
        exporter = LogExportBase()

        # Get report from validator process
        try:
            report = v.validate(paths, interpreter_options=interpreter_options,
                                tool_options=tool_options, split=split)
            exporter.build(report)
        except CatchedException as e:
            logger.error(e)
            # TODO: Exporter should be notified about error on paths
