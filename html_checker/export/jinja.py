# -*- coding: utf-8 -*-
import io
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

import html_checker
from html_checker.export.render import ExporterRenderer
from html_checker.export.jinja_filters import highlight_html_filter


class JinjaExport(ExporterRenderer):
    """
    Exporter with Jinja to produce an HTML report.

    Keyword Arguments:
        template_dir (string): Path to directory which contains template files.
            Default to ``templates`` application directory.

    Attributes:
        TEMPLATES (dict): Each item is an available template where item key is
            the document kind (as given in render context in 'modelize_***'
            methods) and item value the template relative path from template
            directory.
    """
    klassname = __qualname__  # noqa: F821
    FORMAT_NAME = "html"
    DEFAULT_TEMLATE = "basic.html"
    TEMPLATES = {
        "stylesheet": "main.css",
        "audit": "audit.html",
        "summary": "summary.html",
        "report": "report.html",
    }
    DOCUMENT_FILENAMES = {
        "stylesheet": "main.css",
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
        self.jinja_env = self.get_jinjaenv()

        super().__init__(*args, **kwargs)

    def validate(self):
        """
        Ensure template directory is valid.

        Returns:
            string: Returns an error message if any, else ``False``.
        """
        # Directory exists
        if not os.path.exists(self.template_dir):
            msg = "Given template directory does not exists: {}"
            return msg.format(self.template_dir)

        # All required templates exist
        missing_files = []
        for name in sorted(self.TEMPLATES.keys()):
            path = self.TEMPLATES[name]
            if not os.path.exists(os.path.join(self.template_dir, path)):
                missing_files.append(path)
        if len(missing_files) > 0:
            msg = "Some required files are missing from template directory: {}"
            return msg.format(", ".join(missing_files))

        return False

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

        return self.jinja_env.get_template(filepath)

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
        template_name = self.TEMPLATES[context["context"]["kind"]]
        document = self.get_template(template_name)

        return {
            "document": context["document"],
            "content": document.render(**{"export": context["context"]}),
        }

    def release(self, *args, **kwargs):
        """
        Override original method to include 'stylesheet' document which is the
        CSS stylesheet used from templates.
        """
        documents = super().release(*args, **kwargs)

        stylesheet_path = os.path.join(self.template_dir, self.TEMPLATES["stylesheet"])
        with io.open(stylesheet_path, "r") as fp:
            stylesheet = fp.read()

        documents.append({
            "document": self.DOCUMENT_FILENAMES["stylesheet"],
            "content": stylesheet,
        })

        return documents
