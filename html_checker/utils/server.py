import logging

import click

from .. import __pkgname__
from ..exceptions import HtmlCheckerBaseException
from ..serve import ReleaseServer
from .texts import format_hostname


def start_live_release(adress, destination, cherrypy_available, exporter, logger=None,
                       error_klass=None):
    """
    Helper to start the "release server".

    It factorizes server starting process so it can be be shared internally.

    Arguments:
        adress (Path): Network adress to bind server to.
        destination (Path): Directory path to serve.
        cherrypy_available (boolean): Define if CherryPy is installed an available or
            not. If is an error to call this function without CherryPy available, so
            this value should always be true to start a server.
        exporter (exporter.base.ExporterBase): The concrete (not the base one) exporter
            class to use. It is only use to know if current exporter is compatible
            with a server. Currently only the HTML exporter is allowed.

    Keyword Arguments:
        logger (bar): Logging object to use to output errors. The server itself use its
            own logging.
        error_klass (bar): Error exception to raise to abort process when there is an
            error before starting server.

    Returns:
        object: The server instance if started.
    """
    logger = logger or logging.getLogger(__pkgname__)

    # Prepare server interface if required and available
    if cherrypy_available:
        if exporter.FORMAT_NAME != "html":
            logger.critical((
                "Option '--serve' is only available with html exporter."
            ))
            raise click.Abort()

        try:
            serve_address, serve_port = format_hostname(adress)
        except HtmlCheckerBaseException as e:
            logger.critical(e)
            raise click.Abort()

        server = ReleaseServer(
            hostname=serve_address,
            port=serve_port,
            basedir=destination,
            temporary=not destination,
        )
        # Overwrite destination so the temporary directory is set if not empty
        destination = server.basedir

        return server
    else:
        logger.critical((
            "'--serve' option is only available if CherryPy has been "
            "installed."
        ))
        raise click.Abort()
