# -*- coding: utf-8 -*-
import json

from html_checker.export.render import ExporterRenderer


class JsonExport(ExporterRenderer):
    """
    Exporter to produce report documents as JSON.

    Keyword Arguments:
        indent (integer): JSON indentation length. Default is 4 spaces, set it
            to 0 for no indentation but keeping newline or ``None`` for oneline
            without spaces or newlines.
    """
    klassname = __qualname__  # noqa: F821
    FORMAT_NAME = "json"
    DOCUMENT_FILENAMES = {
        "audit": "audit.json",
        "summary": "summary.json",
        "report": "path-{}.json",
    }

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
            "content": json.dumps(context["context"], indent=self.indent,
                                  default=str)
        }
