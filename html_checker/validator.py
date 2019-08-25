import json
import logging
import os
import subprocess
from collections import OrderedDict


import html_checker
from html_checker.exceptions import ReportError, ValidatorError
from html_checker.utils import is_file


class ValidatorInterface:
    """
    Interface for validator tool

    Attributes:
        INTERPRETER (string): Leading interpreter name to execute tool.
        VALIDATOR (string): Path to validator tool to be executed by
            interpreter. It can contain leading ``{HTML_CHECKER}`` pattern to
            be replaced with absolute path to "py-html-checker" install.
        log (logging): Logging object set to application "py-html-checker".
    """
    INTERPRETER = "java"
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

        Arguments:
            paths (list): List of checkable paths to pass to command line.

        Keyword Arguments:
            interpreter_options (list): List of arguments to pass to interpreter.
            tool_options (list): List of arguments to pass to validator tool.

        Returns:
            list: List of items to build full command line.
        """
        args = self.get_interpreter_part(options=interpreter_options)

        html_checker_application = os.path.abspath(
            os.path.dirname(html_checker.__file__)
        )

        if self.VALIDATOR:
            args.append(
                self.VALIDATOR.format(
                    HTML_CHECKER=html_checker_application
                )
            )

        if tool_options:
            for k in tool_options:
                args.append(k)

        args.extend(paths)

        return args

    def build_initial_registry(self, paths):
        """
        Build initial report registry for required paths.

        To fit to validator behaviors, if a path is a file path and exists, it
        will be resolved to its absolute path. If it does not exists, path is
        left unchanged but it will have a log entry for a critical error about
        unexisting file. URL paths are always left unchanged.

        Arguments:
            paths (list): List of page path(s) which have been required for
                checking.

        Returns:
            list: Registry of required path with initial value ``None``,
            except for unexisting file paths which will contain a critical
            error log.
        """
        registry = []

        for path in paths:
            path_key = path
            initial_value = None

            if is_file(path):
                if os.path.exists(path):
                    # Resolve to absolute path
                    path_key = os.path.abspath(path)
                else:
                    initial_value = [{
                        "type": "critical",
                        "message": "File path does not exists."
                    }]

            registry.append((path_key, initial_value))

        return registry

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
        report = OrderedDict(self.build_initial_registry(paths))

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
            # TODO: Remove this or raise it once after loop end for a count of
            # invalid paths (or make it critical ?), remember we need to let
            # logging clean since it is used with default report that is
            # logging output.
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

        Keyword Arguments:
            interpreter_options (list): List of interpreter arguments to
                include in commandline. Default is ``None``.
            tool_options (list): List of validator tool arguments to
                include in commandline. Default is ``None`` but some options
                are defined for internal purposes if not given, such as
                ``--format``, ``--exist-zero-always`` and ``--user-agent``.
                Except the last one, you should not try to change them or you
                will probably break the validator and reporter.

        Returns:
            collections.OrderedDict: Ordered dictionnary of checked pages from
            given path.
        """
        if interpreter_options is None:
            interpreter_options = []
        if tool_options is None:
            tool_options = []

        # Enforce JSON format
        if "--format" not in tool_options:
            tool_options.append("--format")
            tool_options.append("json")

        # Define default user-agent
        if "--user-agent" not in tool_options:
            ua = "Validator.nu/LV py-html-checker/{}"
            tool_options.append("--user-agent")
            tool_options.append(ua.format(html_checker.__version__))

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
