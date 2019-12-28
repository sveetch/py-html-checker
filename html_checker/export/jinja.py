# -*- coding: utf-8 -*-
import datetime
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

import html_checker
from html_checker.exceptions import ExportError
from html_checker.export.base import ExporterBase


class JinjaExport(ExporterBase):
    """
    Exporter with Jinja to produce an HTML report.

    Keyword Arguments:
        template_dir (string): Path to directory which contains template files.
            Default to ``templates`` application directory.
        template (string): Path to the template to use for rendering export.
            Default to value from attribute ``DEFAULT_TEMLATE``.
    """
    klassname = __qualname__
    FORMAT_NAME = "html"
    DEFAULT_TEMLATE = "basic.html"

    def __init__(self, *args, **kwargs):
        template_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(html_checker.__file__),
                "templates",
            )
        )
        self.template_dir = kwargs.pop("template_dir", None) or template_dir
        self.template = kwargs.pop("template", None) or self.DEFAULT_TEMLATE
        self.render_context = {}

        super().__init__(*args, **kwargs)

    def get_jinjaenv(self):
        """
        Start Jinja environment.

        Returns:
            jinja2.Environment: Initialized Jinja environment.
        """
        return Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html", "xml"])
        )

    def get_template(self, filepath):
        """
        Load and return Jinja template.

        Arguments:
            filepath (string): Filepath to the template from its registered
                location in Jinja environment.

        Returns:
            jinja2.Template: Template ready to render.
        """
        jinja_env = self.get_jinjaenv()

        return jinja_env.get_template(filepath)

    def format_row(self, path, row):
        """
        Add path messages to rendering context.

        Arguments:
            path (string): Path related to message.
            row (dict): Dictionnary with every message details.
        """
        coords_keys = ["firstLine", "lastLine", "firstColumn", "lastColumn"]

        level, row = self.parse_row_level(path, row)

        # Keys related to source are formatted and prepared to be moved in
        # "source" item
        source_content = self.format_source_position(row) or {}
        extract = row.pop("extract", None)
        if source_content or extract:
            source_content["extract"] = extract

        context = {k:v for k, v in row.items() if k not in coords_keys}
        context["source"] = source_content

        return context

    def build(self, report):
        """
        Build context to pass to template rendering.

        Arguments:
            report (dict): A dict of path messages, each item key is a path and
                item value is a list of dictionnaries (each dict is a message).
        """
        context = {
            "created": datetime.datetime.now(),
            "items": [],
        }

        for path, messages in report.items():
            self.log.info(path)

            rows = []

            if not messages:
                rows.append({
                    "type": "debug",
                    "message": "There was not any log report for this path.",
                })
            else:
                for row in messages:
                    rows.append(self.format_row(path, row))

            context["items"].append((
                path,
                rows,
            ))

        self.render_context = context

    def release(self, destination=None):
        """
        Release export to an HTML file.
        """
        document = self.get_template(self.template)

        return document.render(**self.render_context)
