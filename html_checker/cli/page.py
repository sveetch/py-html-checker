# -*- coding: utf-8 -*-
import logging

from collections import OrderedDict

import click

try:
    import cherrypy  # noqa: F401
except ImportError:
    CHERRYPY_AVAILABLE = False
else:
    CHERRYPY_AVAILABLE = True

from html_checker.cli.common import COMMON_OPTIONS
from html_checker.exceptions import (HtmlCheckerUnexpectedException,
                                     HtmlCheckerBaseException)
from html_checker.export import get_exporter
from html_checker.validator import ValidatorInterface
from html_checker.utils import reduce_unique, write_documents, resolve_paths


@click.command()
@click.option(*COMMON_OPTIONS["destination"]["args"],
              **COMMON_OPTIONS["destination"]["kwargs"])
@click.option(*COMMON_OPTIONS["exporter"]["args"],
              **COMMON_OPTIONS["exporter"]["kwargs"])
@click.option(*COMMON_OPTIONS["no-stream"]["args"],
              **COMMON_OPTIONS["no-stream"]["kwargs"])
@click.option(*COMMON_OPTIONS["pack"]["args"],
              **COMMON_OPTIONS["pack"]["kwargs"])
@click.option(*COMMON_OPTIONS["safe"]["args"],
              **COMMON_OPTIONS["safe"]["kwargs"])
@click.option(*COMMON_OPTIONS["split"]["args"],
              **COMMON_OPTIONS["split"]["kwargs"])
@click.option(*COMMON_OPTIONS["template-dir"]["args"],
              **COMMON_OPTIONS["template-dir"]["kwargs"])
@click.option(*COMMON_OPTIONS["user-agent"]["args"],
              **COMMON_OPTIONS["user-agent"]["kwargs"])
@click.option(*COMMON_OPTIONS["xss"]["args"],
              **COMMON_OPTIONS["xss"]["kwargs"])
@click.argument('paths', nargs=-1, required=True)
@click.pass_context
def page_command(context, destination, exporter, no_stream, pack, safe, split,
                 template_dir, user_agent, xss, paths):
    """
    Validate given page paths.

    Page path can be an url starting with 'http://' or 'https://' or a file
    path.

    You can give a single page path or many ones to validate. There is multiple
    exporter formats.
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
    exporter_options = {}

    if no_stream:
        tool_options["--no-stream"] = None

    if template_dir:
        exporter_options["template_dir"] = template_dir

    if user_agent:
        tool_options["--user-agent"] = user_agent

    if xss:
        key = "-Xss{}".format(xss)
        interpreter_options[key] = None

    # Start validator interface and exporter instance
    v = ValidatorInterface(exception_class=CatchedException)

    # Start exporter instance
    exporter = get_exporter(exporter)(**exporter_options)
    exporter_error = exporter.validate()
    if exporter_error:
        logger.critical(exporter_error)
        raise click.Abort()
    else:
        if hasattr(exporter, "template_dir"):
            logger.debug("Using template directory: {}".format(exporter.template_dir))

    # Keep packed paths or split them depending 'split' option
    routines = [reduced_paths[:]]
    if split:
        routines = [[v] for v in reduced_paths]

    # Get report from validator process to build export
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

    # Release documents if exporter supports it
    export = exporter.release(pack=pack)

    # Some exporter like logging won't return anything to output or write
    if export:
        if destination:
            # Write every document to files in destination directory
            files = write_documents(destination, export)
            for item in files:
                msg = "Created file: {}"
                logger.info(msg.format(item))
        else:
            # Print out document
            for doc in export:
                click.echo(doc["content"])

    # TODO: Temporary, will be a new arguments
    serve = True
    serve_address = "0.0.0.0"
    serve_port = 8090

    # Report with a destination and correct format
    if serve:
        print("destination:", destination)
        print("exporter.FORMAT_NAME:", exporter.FORMAT_NAME)
        if not destination or exporter.FORMAT_NAME != "html":
            logger.error((
                "Using '--serve' without destination or html exporter does "
                "not have any sense."
            ))
        else:
            server_destination = resolve_paths(destination)

            msg = "Starting http server on: {}"
            logger.info(msg.format(server_destination))

            # Configure webapp server
            cherrypy.config.update({
                'server.socket_host': serve_address,
                'server.socket_port': serve_port,
                'engine.autoreload_on': False,
            })

            # Configure webapp static
            conf = {
                '/': {
                    'tools.staticdir.index': "index.html",
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': server_destination,
                },
            }

            cherrypy.quickstart(None, '/', config=conf)
