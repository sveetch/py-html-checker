import logging

from collections import OrderedDict

import click

try:
    import cherrypy  # noqa: F401
except ImportError:
    CHERRYPY_AVAILABLE = False
else:
    CHERRYPY_AVAILABLE = True

from .. import __pkgname__
from ..exceptions import HtmlCheckerUnexpectedException, HtmlCheckerBaseException
from ..export import get_exporter
from ..utils.documents import write_documents
from ..utils.structures import reduce_unique
from ..utils.server import start_live_release
from ..validator import ValidatorInterface
from .common import COMMON_OPTIONS


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
@click.option(*COMMON_OPTIONS["serve"]["args"],
              **COMMON_OPTIONS["serve"]["kwargs"])
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
def page_command(context, destination, exporter, no_stream, pack, safe, serve,
                 split, template_dir, user_agent, xss, paths):
    """
    Validate given page paths.

    Page path can be an url starting with 'http://' or 'https://' or a file
    path.

    You can give a single page path or many ones to validate. There is multiple
    exporter formats.
    """
    logger = logging.getLogger(__pkgname__)

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

    # NOTE: The server could be started after exporter release but then the temporary
    # directory mode would have been to manage before exporter.
    if serve:
        server = start_live_release(
            serve,
            destination,
            CHERRYPY_AVAILABLE,
            exporter=exporter,
            logger=logger,
            error_klass=click.Abort
        )
        # Assign created temporary directory as the export destination
        destination = server.basedir
    else:
        server = None

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

    # Launch server if any then remove possible temporary content when server
    # has been stopped
    if server:
        server.run()
        server.flush()
