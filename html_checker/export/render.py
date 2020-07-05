# -*- coding: utf-8 -*-
import datetime

import html_checker
from html_checker.export.base import ExporterBase
from html_checker.utils import get_vnu_version, merge_compute


class ExporterRenderer(ExporterBase):
    """
    Exporter with rendering context.

    This is a more advanced exporter than the base one. It build some
    rendering context which can be used to render reports to documents.

    Also it compute some statistic about messages and include them in builded
    context.

    Attributes:
        store (dict): A dictionnary which contain report contents to
            export. It will be filled during build process.
    """
    klassname = __qualname__  # noqa: F821
    FORMAT_NAME = None
    DOCUMENT_FILENAMES = {
        "audit": "audit.txt",
        "summary": "summary.txt",
        "report": "path-{}.txt",
    }

    def __init__(self, *args, **kwargs):
        # Initial global context
        self.store = {
            "metas": {
                "created": datetime.datetime.now(),
                "generator": html_checker.__version__,
                "vnu": get_vnu_version(),
            },
            "reports": [],
        }

        super().__init__(*args, **kwargs)

    def format_row(self, path, row):
        """
        Add path messages to rendering context.

        Arguments:
            path (string): Path related to message.
            row (dict): Dictionnary with every message details.

        Returns:
            dict: Correctly formatted message row context.
        """
        coords_keys = ["firstLine", "lastLine", "firstColumn", "lastColumn"]

        level, row = self.parse_row_level(path, row)

        # Keys related to source are formatted and prepared to be moved in
        # "source" item
        source_content = self.format_source_position(row) or {}
        extract = row.pop("extract", None)
        if source_content or extract:
            source_content["extract"] = extract

        context = {k: v for k, v in row.items() if k not in coords_keys}
        context["source"] = source_content

        return context

    def compute_row_stats(self, stats, row):
        """
        Compute some statistics from given message row.

        Arguments:
            stats (dict): Dict of statistic items to update.
            row (dict): Dictionnary with every message details.

        Returns:
            dict: Updated message row statistics.
        """
        if row["type"] == "debug":
            stats["debugs"] += 1
        elif row["type"] == "error":
            stats["errors"] += 1
        elif row["type"] == "info":
            stats["infos"] += 1
        elif row["type"] == "warning":
            stats["warnings"] += 1

        return stats

    def build(self, report):
        """
        Build context to pass to template rendering for every reported paths.

        Arguments:
            report (dict): A dict of path messages, each item key is a path and
                item value is a list of dictionnaries (each dict is a message
                row).
        """
        for path, messages in report.items():
            # Notify each path in progress to logger
            self.log.info(path)

            rows = []
            stats = {
                "debugs": 0,
                "errors": 0,
                "infos": 0,
                "warnings": 0,
            }

            if not messages:
                row = {
                    "type": "debug",
                    "message": "There was not any log report for this path.",
                }
                stats = self.compute_row_stats(stats, row)
                rows.append(row)
            else:
                for row in messages:
                    context = self.format_row(path, row)
                    stats = self.compute_row_stats(stats, row)
                    rows.append(context)

            # Append path context datas
            self.store["reports"].append((
                path,
                {
                    "messages": rows,
                    "statistics": stats,
                },
            ))

    def get_report_filepath(self, i, name, data):
        """
        Return filepath for a report document.

        Arguments:
            i (int): Index position for document item in building loop.
            name (string): Path name.
            data (dict): Path context.

        Returns:
            string: Document filepath.
        """
        return self.DOCUMENT_FILENAMES["report"].format(i)

    def render(self, context):
        """
        Render a document item.

        This may be used to format or render a document from its given context.

        Arguments:
            context (dict): Document context as returned from
                ``make_***_document`` methods.

        Returns:
            dict: Base method does not perform any render so it just return
                given ``context`` argument unchanged.
        """
        return context

    def modelize_report(self, document_path, context, metas=None):
        """
        Make a report document type.

        Report document display the report statistics and its path messages.

        Arguments:
            document_path (string): Filepath for document to write.
            context (tuple): Path report item with name and data.

        Returns:
            dict: Rendered document. This base method does not render anything
            really so instead it will return document context, something
            like: ::

                {
                    "document": "document filepath",
                    "context": {
                        "kind": "report",
                        "statistics": {}, # Global stats is path stats
                        "name": "path name",
                        "data": {
                            "messages": "Dummy bar",
                            [copy any other carried data]..
                        }
                    }
                }

        """
        name, data = context
        data = data.copy()
        # Move path stats to the top
        stats = data.pop("statistics")

        return self.render({
            "document": document_path,
            "context": {
                "kind": "report",
                "statistics": stats,
                "name": name,
                "metas": metas or {},
                "data": data,
            }
        })

    def modelize_audit(self, document_path, context, metas=None):
        """
        Make an audit document type.

        Audit document display the global statistics (already computed from all
        reports) and display all path reports with their stats.

        Arguments:
            document_path (string): Filepath for document to write.
            context (tuple): Path report item with name and data.

        Returns:
            dict: Rendered document. This base method does not render anything
            really so instead it will return document context, something
            like: ::

                {
                    "document": "document filepath",
                    "context": {
                        "kind": "audit",
                        "statistics": {}, # Global stats from all path stats
                        "data": {
                            [any carried data from item excepted ... items],
                        },
                        "paths": [
                            {
                                "name": "path name",
                                "statistics": {}, # Current path stats
                                "data": {
                                    "messages": "Dummy bar",
                                    [any carried data]..
                                }
                            },
                            [other paths]..
                        ]
                    }
                }

        """
        global_stats = {}
        global_data = {}

        paths = []
        for name, data in context:
            # Move up path stats
            stats = data.pop("statistics")
            # Merge report stats in global stats
            global_stats = merge_compute(stats, global_stats)
            paths.append({
                "name": name,
                "statistics": stats,
                "data": data,
            })

        return self.render({
            "document": document_path,
            "context": {
                "kind": "audit",
                "metas": metas or {},
                "statistics": global_stats,
                "paths": paths,
                "data": global_data or None,
            }
        })

    def modelize_summary(self, document_path, context, metas=None):
        """
        Make a summary document type.

        Summary document display the global statistics (already computed from all
        reports) and list each report documents with their own statistics.

        Arguments:
            document_path (string): Filepath for document to write.
            context (tuple): Path report item with name and data.

        Returns:
            dict: Rendered document. This base method does not render anything
            really so instead it will return document context, something
            like: ::

                {
                    "document": "document filepath",
                    "context": {
                        "kind": "summary",
                        "statistics": {}, # Global stats from all path stats
                        "data": {
                            [any carried data from item excepted ... items],
                        },
                        "paths": [
                            {
                                "name": "path name",
                                "path": "export filepath",
                                "statistics": {}, # Current path stats
                            },
                            [other paths]..
                        ]
                    }
                }

        """
        global_stats = {}

        paths = []
        for i, item in enumerate(context, start=1):
            name, data = item
            # Move up path stats
            stats = data.pop("statistics")
            # Merge report stats in global stats
            global_stats = merge_compute(stats, global_stats)
            paths.append({
                "name": name,
                "path": self.get_report_filepath(i, name, data),
                "statistics": stats,
            })

        return self.render({
            "document": document_path,
            "context": {
                "kind": "summary",
                "metas": metas or {},
                "statistics": global_stats,
                "paths": paths,
            }
        })

    def release(self, *args, **kwargs):
        """
        Make all export documents.

        Keyword Arguments:
            pack (bool): If false, every report will be packed into a single
                document. Else there will be a document for each report.
                Default is ``False``.

        Returns:
            list: List of documents.
        """
        pack = kwargs.pop("pack", False)

        documents = []

        if pack:
            document_path = self.DOCUMENT_FILENAMES["audit"]
            documents.append(self.modelize_audit(
                document_path,
                self.store["reports"],
                self.store["metas"]
            ))
        else:
            for i, context in enumerate(self.store["reports"],
                                        start=1):
                name, data = context
                document_path = self.get_report_filepath(i, name, data)
                documents.append(self.modelize_report(
                    document_path,
                    context,
                    self.store["metas"]
                ))

            documents.append(self.modelize_summary(
                self.DOCUMENT_FILENAMES["summary"],
                self.store["reports"],
                self.store["metas"]
            ))

        return documents
