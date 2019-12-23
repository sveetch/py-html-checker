# -*- coding: utf-8 -*-
import json
import logging

from html_checker.exceptions import ExportError


class LogExportBase:
    """
    Report exporter base.

    Just output every report messages to logging.

    Based on vnu validator behavior from JSON report documentation:

        https://github.com/validator/validator/wiki/Output-%C2%BB-JSON
    """
    LINE_TEMPLATE = ("From line {linestart} column {colstart} to "
                     "line {lineend} column {colend}")
    DIVIDERS = {
        "row": "=====",
        "message": "-",
    }

    def __init__(self, dividers=None):
        self.log = logging.getLogger("py-html-checker")

        self.dividers = dividers
        if self.dividers is None:
            self.dividers = self.DIVIDERS

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
        if "lastLine" not in row:
            return None

        firstLine = row["lastLine"]
        if "firstLine" in row:
            firstLine = row["firstLine"]

        firstColumn = row["lastColumn"]
        if "firstColumn" in row:
            firstColumn = row["firstColumn"]

        line_msg = self.LINE_TEMPLATE.format(
            linestart=firstLine,
            lineend=row["lastLine"],
            colstart=firstColumn,
            colend=row["lastColumn"],
        )

        return line_msg

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
                # Row divider
                if self.dividers.get("message", None):
                    self.log.debug(self.dividers.get("message"))

                # Until we faced every case from validator logs to be sure to not
                # miss any edge case
                if "type" not in row:
                    print(json.dumps(path, indent=4))
                    raise NotImplementedError

                # Output message following its type
                if row["type"] in ["error", "critical", "non-document-error"]:
                    self.output_row(self.log.error, row)
                elif row["type"] == "info" and row.get("subType", None) == "warning":
                    self.output_row(self.log.warning, row)
                elif row["type"] == "info":
                    self.output_row(self.log.debug, row)
                else:
                    raise ExportError("Unexpected message type:\n{}".format(
                        json.dumps(row, indent=4)
                    ))

    def release(self):
        """
        Release export.

        The default method does not do anything since it is a logging exporter
        which directly release messages once built from ``LogExportBase.build``.
        """
        pass
