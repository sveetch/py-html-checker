# -*- coding: utf-8 -*-
import logging

from collections import OrderedDict

import click

from html_checker.cli.common import COMMON_OPTIONS
from html_checker.exceptions import (HtmlCheckerUnexpectedException,
                                     HtmlCheckerBaseException)
from html_checker.export import LogExportBase
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
@click.argument('paths', nargs=-1, required=True)
@click.pass_context
def page_command(context, xss, no_stream, user_agent, safe, split, paths):
    """
    Validate pages from given paths.

    Path can be an url starting with 'http://' or 'https://' or a file path.

    You can give many paths to validate each one.
    """
    logger = logging.getLogger("py-html-checker")

    # Ensure to always check a same path only once
    reduced_paths = reduce_unique(paths)

    if len(paths) > len(reduced_paths):
        msg = ("Launching validation for {reduced} paths ({tweens} "
               "ignored duplications)")
        logger.info(msg.format(**{
            "reduced": len(reduced_paths),
            "tweens": len(paths) - len(reduced_paths),
        }))
    else:
        msg = "Launching validation for {} paths"
        logger.info(msg.format(len(reduced_paths)))

    # Safe mode enabled, catch all internal exceptions
    if safe:
        CatchedException = HtmlCheckerBaseException
    # Safe mode disabled, watch for a dummy exception that won't never occurs
    # so internal exception are still raised
    else:
        CatchedException = HtmlCheckerUnexpectedException

    # Tools options
    interpreter_options = OrderedDict([])
    tool_options = OrderedDict([])

    if no_stream:
        tool_options["--no-stream"] = None

    if user_agent:
        tool_options["--user-agent"] = user_agent

    if xss:
        key = "-Xss{}".format(xss)
        interpreter_options[key] = None

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
