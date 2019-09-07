# -*- coding: utf-8 -*-
import logging

from collections import OrderedDict

import click

from html_checker.cli.common import COMMON_OPTIONS, validate_paths
from html_checker.export import LogExportBase
from html_checker.validator import ValidatorInterface


@click.command()
@click.option(*COMMON_OPTIONS["xss"]["args"],
              **COMMON_OPTIONS["xss"]["kwargs"])
@click.option(*COMMON_OPTIONS["no-stream"]["args"],
              **COMMON_OPTIONS["no-stream"]["kwargs"])
@click.option(*COMMON_OPTIONS["user-agent"]["args"],
              **COMMON_OPTIONS["user-agent"]["kwargs"])
@click.argument('paths', nargs=-1, required=True)
@click.pass_context
def page_command(context, xss, no_stream, user_agent, paths):
    """
    Validate pages from given paths.

    Path can be an url starting with 'http://' or 'https://' or a file path.

    You can give many paths to validate each one.
    """
    logger = logging.getLogger("py-html-checker")

    logger.debug("Launching validation for {} paths".format(len(paths)))

    # Validate paths
    errors = validate_paths(logger, paths)
    if errors > 0:
        raise click.Abort()

    # Compile options
    interpreter_options = OrderedDict([])
    tool_options = OrderedDict([])

    if no_stream:
        tool_options["--no-stream"] = None

    if user_agent:
        tool_options["--user-agent"] = user_agent

    if xss:
        key = "-Xss{}".format(xss)
        interpreter_options[key] = None

    # Get report from validator process
    v = ValidatorInterface()
    report = v.validate(paths, interpreter_options=interpreter_options,
                        tool_options=tool_options)

    # print()
    # print(json.dumps(report, indent=4))
    # print()

    # Export report
    exporter = LogExportBase()
    exporter.build(report)
