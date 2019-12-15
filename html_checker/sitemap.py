import io
import json
import logging
import os
import mimetypes
import re
from xml.etree import ElementTree

import requests
from requests.exceptions import RequestException

from html_checker import USER_AGENT
from html_checker.utils import is_local_ressource
from html_checker.exceptions import PathInvalidError, SitemapInvalidError


class Sitemap:
    """
    Sitemap reader is able to get and read sitemap from a file path or an url
    either in XML or JSON format.
    """
    def __init__(self, register=None, user_agent=None):
        self.register = register
        self.user_agent = user_agent or USER_AGENT
        self.log = logging.getLogger("py-html-checker")

    def get_headers(self):
        """
        Return headers to pass through request.

        Returns:
            dict: Dictionnary of headers.
        """
        return {
            "User-Agent": self.user_agent,
        }

    def contenttype(self, path):
        """
        Return the contenttype for given path.

        Arguments:
            path (string): Ressource path.

        Returns:
            string: The content type keyword if valid, else None.
        """
        guessed = mimetypes.guess_type(path)

        if not guessed or guessed == (None, None):
            msg = "Unable to guess content-type from given path."
            raise PathInvalidError(msg)

        contenttype, encoding = guessed

        if contenttype == "application/json":
            return "json"
        elif contenttype == "application/xml":
            return "xml"

        msg = "Guessed content-type is not supported: {}"
        raise PathInvalidError(msg.format(contenttype))

    def get_file_ressource(self, path):
        """
        Open given file and return its content.

        Arguments:
            path (string): Ressource file path.

        Returns:
            string: File content.
        """
        if not os.path.exists(path):
            msg = "Given file path does not exists: {}"
            raise PathInvalidError(msg.format(path))

        with io.open(path, "r") as fp:
            content = fp.read()

        return content

    def get_url_ressource(self, path):
        """
        Open given url and return its content.

        Arguments:
            path (string): Ressource url.

        Returns:
            string: Document content.
        """
        try:
            r = requests.get(path, headers=self.get_headers())
        except RequestException as e:
            msg = "Unable to reach sitemap url: {}"
            raise PathInvalidError(msg.format(e))

        if r.status_code != 200:
            msg = "Sitemap request returned invalid status: {}"
            raise PathInvalidError(msg.format(r.status_code))

        return r.content

    def parse_sitemap_json(self, ressource):
        """
        Parse JSON sitemap

        Arguments:
            ressource (string): Ressource content.

        Returns:
            list: List of paths.
        """
        try:
            content = json.loads(ressource)
        except json.decoder.JSONDecodeError as e:
            msg = "Invalid JSON sitemap: {}"
            raise SitemapInvalidError(msg.format(e))

        if "urls" not in content:
            msg = "Invalid JSON sitemap, it must contains an 'urls' list of urls."
            raise SitemapInvalidError(msg)

        return content["urls"]

    def parse_sitemap_xml(self, ressource):
        """
        Parse XML sitemap

        Arguments:
            ressource (string): Ressource content.

        Returns:
            list: List of paths.
        """
        paths = []

        try:
            root = ElementTree.fromstring(ressource)
        except ElementTree.ParseError as e:
            msg = "Invalid XML sitemap: {}"
            raise SitemapInvalidError(msg.format(e))

        # Catch the root namespace if any
        ns = re.match(r'{.*}', root.tag)
        if ns:
            ns = ns.group(0)
        else:
            ns = ""

        if root.tag.replace(ns, "") != "urlset":
            msg = "Invalid XML sitemap, cannot find root element <urlset>"
            raise SitemapInvalidError(msg)

        warnings = 0
        for item in root.iter('{}url'.format(ns)):
            location = item.find("{}loc".format(ns))

            if location is None:
                warnings += 1
            else:
                paths.append(location.text)

        if warnings > 0:
            msg = "There was {} url item(s) without a <loc> element."
            self.log.warning(msg.format(warnings))

        return paths

    def get_urls(self, path):
        """
        Parse given sitemap to get urls.

        Arguments:
            path (string): Sitemap path.

        Returns:
            list: List of urls.
        """
        if is_local_ressource(path):
            ressource = self.get_file_ressource(path)
        else:
            ressource = self.get_url_ressource(path)

        contenttype = self.contenttype(path)

        if contenttype == "json":
            return self.parse_sitemap_json(ressource)
        elif contenttype == "xml":
            return self.parse_sitemap_xml(ressource)
        # Should never occurs
        else:
            msg = ("Unable to parse ressource from given path, unknowed "
                   "content type: {}".format(contenttype))
            raise SitemapInvalidError(msg)
