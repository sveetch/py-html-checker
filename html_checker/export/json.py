# -*- coding: utf-8 -*-
import json

import html_checker
from html_checker.exceptions import ExportError
from html_checker.export.render import ExporterRenderer


class JsonExport(ExporterRenderer):
    """
    Exporter to produce report documents as JSON.
    """
    klassname = __qualname__
    FORMAT_NAME = "json"

    def __init__(self, *args, **kwargs):
        self.indent = kwargs.pop("indent", 4)

        super().__init__(*args, **kwargs)

    def render(self, context):
        """
        Render document to JSON.

        Rendered document is serialized to JSON string inside ``content``
        item in document dict.

        Arguments:
            context (dict): Document context as returned from
                ``modelize_***`` methods.

        Returns:
            dict: The document ``context`` with its serialization inside
            ``content`` item.
        """
        return {
            "document": context["document"],
            "content": json.dumps(context["context"], indent=self.indent)
        }
