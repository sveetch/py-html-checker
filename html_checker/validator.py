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
    INTERPRETER = "java" # Leading interpreter to execute tool
    VALIDATOR = "{HTML_CHECKER}/vnujar/vnu.jar" # Validator tool to be executed by interpreter

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

    def get_validator_command(self, path, interpreter_options=None,
                              tool_options=None):
        """
        Build full command line to execute validator on given path.
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

        args.append(path)

        return args

    def parse_report(self, paths, content):
        """
        From given validator report return an usable and normalized report.

        Arguments:
            paths (list): List of page path(s) which have been checked by
                validator.
            content (string): Report return from validator, a JSON string is
                expected.

        Returns:
            list: List of report for checked paths.
        """
        # Build initial registry of path reports
        report = OrderedDict([(item, None) for item in paths])

        content = content.decode("utf-8").strip()

        try:
            content = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            msg = "Invalid JSON report: {}"
            raise ReportError(msg.format(e))

        if "messages" not in content:
            msg = ("Invalid JSON validator report, it must contains a "
                   "'messages' list of checked pages.")
            raise ReportError(msg)

        for item in content["messages"]:
            path = item.get("url")
            item.pop("url")
            if path in report:
                if report[path] == None:
                    report[path] = []
                report[path].append(item)
            else:
                msg = "Validator report contains unknow path '{}'"
                self.log.warning(msg.format(path))

        return report

    def validate(self, path, interpreter_options=None,
                 tool_options=None):
        """
        Perform validation with validator tool for given path.

        Arguments:
            path (string): Path of page(s) to validate.

        Returns:
            collections.OrderedDict: Ordered dictionnary of checked pages from
            given path.
        """
        # Path argument can contain one or many paths, however we always store
        # it as a list for report
        paths = path.split()

        # Enforce JSON format
        if "--format" not in tool_options:
            tool_options.append("--format")
            tool_options.append("json")

        # Enforce non error exit so validator report always goes to the stdout
        tool_options.append("--exit-zero-always")

        command = self.get_validator_command(
            path,
            interpreter_options=interpreter_options,
            tool_options=tool_options
        )

        # NOTE: vnu does not throw error on unexisting files but still have
        # error for invalid urls. Have to manage this case with reports
        try:
            process = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except FileNotFoundError as e:
            raise ValidatorError("Unable to reach interpreter to run validator: {}".format(e))
        except subprocess.CalledProcessError as e:
            raise ValidatorError("Validator execution failed: {}".format(e.output.decode("utf-8")))

        return self.parse_report(paths, process)
