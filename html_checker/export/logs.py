# -*- coding: utf-8 -*-
from html_checker.export.base import ExporterBase


class LoggingExport(ExporterBase):
    """
    Logging exporter.

    Output directly every report messages to logging.

    Keyword Arguments:
        dividers (dict): Dict of available dividers string use to divide
            content. It have to contain an item for ``row`` and ``message``.
            Default to value from attribute ``DIVIDERS``.
    """
    klassname = __qualname__  # noqa: F821
    FORMAT_NAME = "logging"
    LINE_TEMPLATE = ("From line {linestart} column {colstart} to "
                     "line {lineend} column {colend}")
    DIVIDERS = {
        "row": "=====",
        "message": "-",
    }

    def __init__(self, *args, **kwargs):
        self.dividers = kwargs.pop("dividers", None)

        if self.dividers is None:
            self.dividers = self.DIVIDERS

        super().__init__(*args, **kwargs)

    def format_extract(self, row):
        """
        Return formatted string for extracted code related to message.

        This escape whitespaces to ensure they do not mess the log output.

        Arguments:
            row (dict): Dictionnary with every message details.

        Returns:
            string: Formated string for extracted code if any or None.
        """
        if "extract" in row:
            return row["extract"].replace("\n", "\\n").replace("\r", "\\r")\
                    .replace("\t", "\\t")

        return None

    def format_source_position(self, row):
        """
        Return formatted string for position infos about a source code.

        A row without "lastLine" item is assumed to not have any position
        informations.

        If empty, the default value for "firstLine" is the "lastLine" value.
        In the same way, default value for "firstColumn" is the "lastColumn"
        value.

        Arguments:
            row (dict): Dictionnary with every message details.

        Returns:
            string: Formated string including positions infos if any or None.
        """
        context = super().format_source_position(row)

        if context is None:
            return None

        return self.LINE_TEMPLATE.format(**context)

    def output_row(self, method, row):
        """
        Format and output row content.

        Arguments:
            row (dict): Dictionnary with every message details.
            method (function): Function to output formatted content.
        """
        line_msg = self.format_source_position(row)
        if line_msg:
            method(line_msg)

        # Message is expected to always be present
        method(row["message"])

        extract = self.format_extract(row)
        if extract:
            method(extract)

    def build(self, report):
        """
        Build report export.

        Arguments:
            report (dict): A dict of path messages, each item key is a path and
                item value is a list of dictionnaries (each dict is a message).
        """
        for path, messages in report.items():
            if self.dividers.get("row", None):
                self.log.debug(self.dividers.get("row"))

            self.log.info(path)

            if not messages:
                self.log.debug("There was not any log report for this path.")
                continue

            for row in messages:
                # Row divider is directly outputted to logging at debug level
                if self.dividers.get("message", None):
                    self.log.debug(self.dividers.get("message"))

                level, row = self.parse_row_level(path, row)
                self.output_row(getattr(self.log, level), row)
