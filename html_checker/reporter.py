# -*- coding: utf-8 -*-
import json
import logging
import os
from collections import OrderedDict

from html_checker.exceptions import ReportError
from html_checker.utils import is_local_ressource


class ReportStore:
    """
    Reporter model.

    Parse validator report content and store it correctly.
    """
    def __init__(self, paths):
        self.log = logging.getLogger("py-html-checker")

        self.paths = paths
        self.registry = OrderedDict(
            self.initial_registry(self.paths)
        )

    def initial_registry(self, paths):
        """
        Build initial report registry from given paths.

        To fit to validator behaviors, if a path is an existing local file path
        will be resolved to its absolute path. If it does not exists or an URL
        it is left unchanged.

        Arguments:
            paths (list): List of page path(s) which have been required for
                checking.

        Returns:
            list: Registry of required path with initial value ``None``,
            except for unexisting file paths which will contain a critical
            error log.
        """
        registry = []

        for path in paths:
            path_key = path

            if is_local_ressource(path):
                if os.path.exists(path):
                    path_key = os.path.abspath(path)

            registry.append((path_key, None))

        return registry

    def parse(self, content):
        """
        Parse given JSON string to return a Python object.

        Content must be a valid JSON string (byte or not) like this: ::

            {"messages":[{"url": "http://perdu.com", "type": "info"}]}

        It must be compatible with expected dict format from method
        ``ReportStore.add``.

        Arguments:
            content (string): Report returned from validator, a JSON string is
                expected.

        Returns:
            object: Object decoded from JSON string.
        """
        # Decode returned byte string from process output JSON
        content = content.decode("utf-8").strip()

        # Try to load and validate report JSON
        try:
            content = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            msg = "Invalid JSON report: {}"
            raise ReportError(msg.format(e))
        else:
            if "messages" not in content:
                msg = ("Invalid JSON report: it must contains a 'messages' item "
                       "of checked page list.")
                raise ReportError(msg)

        return content

    def add(self, content, raw=True):
        """
        Add report messages from given content to registry.

        Arguments:
            content (string or list): JSON string of messages or list of message
                dictionnaries, depending ``raw`` argument.

        Keyword Arguments:
            raw (bool): If true, will parse content as a JSON string, this is
                the default behavior. If false, content is assumed to be a
                list of dictonnary for each message.
        """
        if raw:
            payload = self.parse(content)
            messages = payload["messages"]
        else:
            messages = content

        # To retain already outputed error messages for unknow paths
        already_seen_errors = []

        # Walk report to find message about required path to check and store
        # them
        for item in messages:
            path = item.get("url")
            item.pop("url")

            # Clean prefix file path from reported path
            if path.startswith("file:"):
                path = path[len("file:"):]

            if path in self.registry:
                if self.registry[path] is None:
                    self.registry[path] = []
                self.registry[path].append(item)
            else:
                msg = "Validator report contains unknow path '{}'".format(path)
                if msg not in already_seen_errors:
                    already_seen_errors.append(msg)
                    self.log.warning(msg)
