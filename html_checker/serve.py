import logging

import cherrypy

from html_checker.exceptions import HTTPServerError
from html_checker.utils import resolve_paths


class ReleaseServer:
    """
    Server to serve report release.

    Attributes:
        log (logging): Logging object set to application "py-html-checker".
    """
    def __init__(self, hostname, port, basedir=None, temporary=False):
        self.log = logging.getLogger("py-html-checker")
        self.hostname = hostname
        self.port = port
        self.basedir = self.get_basedir(basedir, temporary)
        self.temporary = temporary


    def get_basedir(self, path, temporary):
        """
        Get the base directory path to server.

        Return an absolute path. Possibly create a temporary directory if
        temporary mode is enabled.
        """
        if not path and not temporary:
            msg = (
                "A base directory is required if temporary mode is not enabled."
            )
            raise HTTPServerError(msg)

        return basedir

    def get_server_config(self):
        """
        Return the server config to set on CherryPy.
        """
        return {
            "server.socket_host": self.hostname,
            "server.socket_port": self.port,
            "engine.autoreload_on": False,
        }

    def get_app_config(self):
        """
        Return the application config to set on mounted application.
        """
        return {
            '/': {
                'tools.staticdir.index': "index.html",
                'tools.staticdir.on': True,
                'tools.staticdir.dir': self.basedir,
            },
        }

    def flush(self):
        """
        Flush a builded release.
        """
        return self.basedir

    def run(self):
        """
        Run CherryPy instance on release
        """
        msg = "Starting http server on: {}"
        self.log.info(msg.format(self.basedir))

        cherrypy.config.update(self.get_server_config())
        cherrypy.quickstart(None, "/", config=self.get_app_config())

        if self.temporary:
            self.flush()
