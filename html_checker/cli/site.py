# -*- coding: utf-8 -*-
import logging

from collections import OrderedDict

import click

from html_checker.cli.common import COMMON_OPTIONS, validate_sitemap_path
from html_checker.exceptions import (HtmlCheckerUnexpectedException,
                                     HtmlCheckerBaseException)
from html_checker.export import LogExportBase
from html_checker.sitemap import Sitemap
from html_checker.validator import ValidatorInterface
from html_checker.utils import reduce_unique


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
@click.option('--sitemap-only', is_flag=True,
              help=("Download and parse given Sitemap ressource and output "
                    "informations but never try to valide its items."))
@click.argument('path', required=True)
@click.pass_context
def site_command(context, xss, no_stream, user_agent, safe, split, path,
                 sitemap_only):
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
    sitemap_file_status = validate_sitemap_path(logger, path)
    if not sitemap_file_status:
        raise click.Abort()

    # Initial tools options
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

    # Ensure to always check a same path only once
    reduced_paths = reduce_unique(paths)

    if len(paths) > len(reduced_paths):
        msg = "Sitemap have {reduced} paths (plus {tweens} ignored duplications)"
        logger.info(msg.format(**{
            "reduced": len(reduced_paths),
            "tweens": len(paths) - len(reduced_paths),
        }))
    else:
        logger.info("Sitemap have {} paths".format(len(reduced_paths)))

    # Proceed to path validations
    if not sitemap_only:
        logger.debug("Launching validation for sitemap items")

        # Start validator interface and exporter instances
        v = ValidatorInterface(exception_class=CatchedException)
        exporter = LogExportBase()

        # Keep packed paths or split them depending 'split' option
        routines = [reduced_paths[:]]
        if split:
            routines = [[v] for v in reduced_paths]

        # Get report from validator process
        for item in routines:
            try:
                report = v.validate(item, interpreter_options=interpreter_options,
                                    tool_options=tool_options)
                exporter.build(report.registry)
            except CatchedException as e:
                exporter.build({
                    "all": [{
                        "type": "critical",
                        "message": e,
                    }]
                })

        exporter.release()
    # Don't valid anything just list paths
    else:
        logger.debug("Listing available paths from sitemap")

        # Count digits from total path counter
        digits = len(str(len(reduced_paths)))

        for i, item in enumerate(reduced_paths, start=1):
            # Justify indice number with zero(s)
            indice = str(i).rjust(digits, "0")
            logger.info("{}) {}".format(indice, item))
