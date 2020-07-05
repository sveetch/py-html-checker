# -*- coding: utf-8 -*-
import json
import logging

from html_checker.exceptions import ExportError


class ExporterBase(object):
    """
    Exporter base.

    Don't output or write anything, just contain shared methods

    Message parsing is based on vnu validator behavior from JSON report
    documentation:

        https://github.com/validator/validator/wiki/Output-%C2%BB-JSON
    """
    FORMAT_NAME = None
    # Required to be paste in every exporter class
    klassname = __qualname__  # noqa: F821

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger("py-html-checker")

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

        return {
            "linestart": firstLine,
            "lineend": row["lastLine"],
            "colstart": firstColumn,
            "colend": row["lastColumn"],
        }

    def parse_row_level(self, path, row):
        """
        Parse a report message row.

        Arguments:
            message (dict): A dict of path messages, each item key is a path and
                item value is a list of dictionnaries (each dict is a message).
        """
        # Until we faced every case from validator logs to be sure to not
        # miss any edge case
        if "type" not in row:
            print(json.dumps(path, indent=4))
            raise NotImplementedError

        # Non validating error
        if row["type"] in ["critical", "non-document-error"]:
            row["type"] = "error"
            if "subType" in row:
                del row["subType"]
            return "error", row
        # Natural basic error
        elif row["type"] == "error":
            return "error", row
        # Actually vnu keep containing warning a subtype of an info level
        elif row["type"] == "info" and row.get("subType", None) == "warning":
            row["type"] = "warning"
            del row["subType"]
            return "warning", row
        # May not be really used but in case of evolution from vnu
        elif row["type"] == "warning":
            return "warning", row
        elif row["type"] == "info":
            return "info", row
        else:
            raise ExportError("Unexpected message type:\n{}".format(
                json.dumps(row, indent=4)
            ))

    def build(self, report):
        """
        Build report export.

        Just demonstrate walking through messages rows to parse them.

        Arguments:
            report (dict): A dict of path messages, each item key is a path and
                item value is a list of dictionnaries (each dict is a message).
        """
        for path, messages in report.items():
            self.log.info(path)

            if not messages:
                self.log.debug("There was not any log report for this path.")
                continue

            for row in messages:
                level, row = self.parse_row_level(path, row)

    def validate(self):
        """
        A validation method for some exporter which needs to validate some
        environment or parameters. This base method does not perform any check.

        Returns:
            string: Should return an error message if any, else ``False``.
        """
        return False

    def release(self, *args, **kwargs):
        """
        Release export.

        This base method does not do anything, it only exists to support
        identical signature from all exporters.
        """
        pass
