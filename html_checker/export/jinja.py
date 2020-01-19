# -*- coding: utf-8 -*-
import datetime
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

import html_checker
from html_checker.exceptions import ExportError
from html_checker.export.render import ExporterRenderer
from html_checker.export.jinja_filters import highlight_html_filter
from html_checker.utils import get_vnu_version


class JinjaExport(ExporterRenderer):
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
    DOCUMENT_FILENAMES = {
        "audit": "index.html",
        "summary": "index.html",
        "report": "path-{}.html",
    }

    def __init__(self, *args, **kwargs):
        template_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(html_checker.__file__),
                "templates",
            )
        )
        self.template_dir = kwargs.pop("template_dir", None) or template_dir
        self.template = kwargs.pop("template", None) or self.DEFAULT_TEMLATE

        super().__init__(*args, **kwargs)

    def get_jinjaenv(self):
        """
        Start Jinja environment.

        Returns:
            jinja2.Environment: Initialized Jinja environment.
        """
        env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html", "xml"])
        )
        env.filters["highlight_html"] = highlight_html_filter
        return env

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

    def release(self):
        """
        Release export to an HTML file.

        TODO: Old way release method, not up to date with export renderer
        which should return a list of rendered documents. If any writing file
        is required it has to be done outside of release (like in the CLI).
        """
        document = self.get_template(self.template)

        return document.render(**self.render_context)
