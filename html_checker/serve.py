import logging
import shutil
import tempfile

import cherrypy

from html_checker.exceptions import HTTPServerError
from html_checker.utils import resolve_paths


class ReleaseServer:
    """
    Server to serve report release.

    Arguments:
        hostname (string): Hostname for bind adress.
        port (integer): Port integer for bind adress. If empty the default value will
            be ``8000``.

    Keyword Arguments:
        basedir (string): Directory to serve contents. It can only be null if temporary
            mode is enabled else it is an error.
        temporary (boolean): If true built report will be done in a temporary
            directory to delete on server is stopped. It is an error to define
            a basedir value and enable temporary mode.

    Attributes:
        log (logging): Logging object set to application "py-html-checker".
    """
    DEFAULT_PORT = 8000

    def __init__(self, hostname, port, basedir=None, temporary=False):
        self.log = logging.getLogger("py-html-checker")
        self.hostname = hostname
        self.port = port or self.DEFAULT_PORT
        self.basedir = self.get_basedir(basedir, temporary)
        self.temporary = temporary

    def get_basedir(self, path, temporary):
        """
        Get the base directory path to serve.

        Just serve the given path if any, else if temporary mode is enabled a
        temporary directory will be created and assigned as the base directory.
        Remember to use the ``flush`` method to clean the temporary directory
        when you are done with it.

        Giving a path and enable temporary mode cause a conflict because for
        security reason we don't support to assume an existing directory as a
        temporary directory to clean.

        Arguments:
            path (string): Path to serve as base directory, it will be resolved
                as an absolute path.
            temporary (boolean): To enable or disable temporary.

        Raises:
            html_checker.exceptions.HTTPServerError: Raised if there is conflict
                between given path and temporary mode.

        Returns:
            string: Absolute path for base directory. Either the given one or
            a temporary directory just created.
        """
        if not path:
            if not temporary:
                msg = (
                    "A base directory is required if temporary mode is not "
                    "enabled."
                )
                raise HTTPServerError(msg)
            else:
                basedir = tempfile.mkdtemp(prefix="py-html-checker_report")
        else:
            if temporary:
                msg = (
                    "Temporary mode can not be enabled if a base directory has "
                    "been given."
                )
                raise HTTPServerError(msg)
            else:
                basedir = resolve_paths(path)

        return basedir

    def get_server_config(self):
        """
        Return the server config to set on CherryPy.

        Returns:
            dict: Server configuration.
        """
        return {
            "server.socket_host": self.hostname,
            "server.socket_port": self.port,
            "engine.autoreload_on": False,
        }

    def get_app_config(self):
        """
        Return the application config to set on mounted application.

        Returns:
            dict: Application configuration.
        """
        return {
            "/": {
                "tools.staticdir.index": "index.html",
                "tools.staticdir.on": True,
                "tools.staticdir.dir": self.basedir,
            },
        }

    def flush(self):
        """
        Flush a builded release.

        Returns:
            string: Removed path if temporary mode is enabled, else None.
        """
        removed = None

        if self.temporary:
            msg = "Clean temporary directory: {}"
            self.log.debug(msg.format(self.basedir))

            shutil.rmtree(self.basedir)
            removed = self.basedir

        return removed

    def run(self):
        """
        Run CherryPy instance on release.
        """
        msg = "Starting HTTP server on: {}:{}".format(self.hostname, self.port)
        self.log.info(msg.format(self.basedir))

        msg = "Serving report from: {}"
        self.log.debug(msg.format(self.basedir))

        self.log.warning("Use CTRL+C to terminate.")

        cherrypy.config.update(self.get_server_config())
        cherrypy.quickstart(None, "/", config=self.get_app_config())
