import json
import logging
import os
import subprocess
from collections import OrderedDict


import html_checker
from html_checker.exceptions import ReportError, ValidatorError


class ValidatorInterface:
    """
    Interface for validator tool
    """
    # Leading interpreter to execute tool
    INTERPRETER = "java"
    # Validator tool to be executed by interpreter
    VALIDATOR = "{HTML_CHECKER}/vnujar/vnu.jar"

    def __init__(self):
        self.log = logging.getLogger("py-html-checker")

    def get_interpreter_part(self, options=None):
        """
        Return the command line interpreter part (its name then options).

        Keyword Arguments:
            options (list): List of interpreter arguments to include.

        Returns:
            list: List of items to build command line for interpreter (name
            and possible options).
        """
        args = []

        if self.INTERPRETER:
            args.append(self.INTERPRETER)

        if options:
            for k in options:
                args.append(k)

        if self.INTERPRETER == "java":
            args.append("-jar")

        return args

    def get_validator_command(self, paths, interpreter_options=None,
                              tool_options=None):
        """
        Build full command line to execute validator tool on given path list.
        """
        args = self.get_interpreter_part(options=interpreter_options)

        html_checker_application = os.path.abspath(
            os.path.dirname(html_checker.__file__)
        )

        if self.VALIDATOR:
            args.append(self.VALIDATOR.format(HTML_CHECKER=html_checker_application))

        if tool_options:
            for k in tool_options:
                args.append(k)

        args.extend(paths)

        return args

    def parse_report(self, paths, content):
        """
        From given validator report return an usable and normalized report.

        Arguments:
            paths (list): List of page path(s) which have been required for
                checking.
            content (string): Report return from validator, a JSON string is
                expected.

        Returns:
            list: List of reports for checked paths.
        """
        # Build initial registry of path reports
        report = OrderedDict([(item, None) for item in paths])

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
                msg = ("Invalid JSON validator report, it must contains a "
                       "'messages' list of checked pages.")
                raise ReportError(msg)

        # Walk report to find message about required path to check and store
        # them
        for item in content["messages"]:
            path = item.get("url")
            item.pop("url")

            # Clean prefix file path from reported path
            if path.startswith("file:"):
                path = path[len("file:"):]

            if path in report:
                if report[path] is None:
                    report[path] = []
                report[path].append(item)
            else:
                msg = "Validator report contains unknow path '{}'"
                self.log.warning(msg.format(path))

        return report

    def validate(self, paths, interpreter_options=None,
                 tool_options=None):
        """
        Perform validation with validator tool for given path.

        Arguments:
            paths (list): List of page path to validate.

        Returns:
            collections.OrderedDict: Ordered dictionnary of checked pages from
            given path.
        """
        # Enforce JSON format
        if "--format" not in tool_options:
            tool_options.append("--format")
            tool_options.append("json")

        # Enforce non error exit in order that validator report always goes to
        # the stdout so we can capture it
        if "--exit-zero-always" not in tool_options:
            tool_options.append("--exit-zero-always")

        # Build command line from options
        command = self.get_validator_command(
            paths,
            interpreter_options=interpreter_options,
            tool_options=tool_options
        )

        # Execute command process
        try:
            process = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except FileNotFoundError as e:
            msg = "Unable to reach interpreter to run validator: {}"
            raise ValidatorError(msg.format(e))
        except subprocess.CalledProcessError as e:
            msg = "Validator execution failed: {}"
            raise ValidatorError(msg.format(e.output.decode("utf-8")))

        return self.parse_report(paths, process)
