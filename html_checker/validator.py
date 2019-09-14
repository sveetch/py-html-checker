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

    def compile_options(self, options):
        """
        Compile options to a list.

        Arguments:
            options (dict): A dict or a OrderedDict of options to
                compile to a list of arguments. Option values can be either a
                string or a list.

        Returns:
            list: List of options arguments.
        """
        opts = []

        for name, value in options.items():
            if name:
                opts.append(name)

            if value:
                if isinstance(value, list) or isinstance(value, tuple):
                    opts.extend(value)
                else:
                    opts.append(value)

        return opts

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
            args.extend(self.compile_options(options))

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
            args.extend(self.compile_options(tool_options))

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

    def execute_validator(self, command):
        """
        Execute validator process from given command.

        Arguments:
            command (list): List of command elements.

        Returns:
            subprocess.CompletedProcess: Process output.
        """
        try:
            process = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except FileNotFoundError as e:
            msg = "Unable to reach interpreter to run validator: {}"
            raise ValidatorError(msg.format(e))
        except subprocess.CalledProcessError as e:
            msg = "Validator execution failed: {}"
            raise ValidatorError(msg.format(e.output.decode("utf-8")))

        return process

    def manage_options(self, interpreter_options, tool_options):
        """
        Compile default and additional interpreter and validator options.

        Arguments:
            interpreter_options (dict): Dict of interpreter arguments to
                include in commandline. Default is ``None``.
            tool_options (dict): Dict of validator tool arguments to
                include in commandline. Default is ``None`` but some options
                are defined for internal purposes if not given, such as
                ``--format``, ``--exist-zero-always`` and ``--user-agent``.
                Except the last one, you should not try to change them or you
                will probably break the validator and reporter.

        Returns:
            tuple: Interpreter and validator option lists in a tuple.
        """
        if interpreter_options is None:
            interpreter_options = OrderedDict([])
        if tool_options is None:
            tool_options = OrderedDict([])

        # Enforce JSON format
        if "--format" not in tool_options:
            tool_options["--format"] = "json"

        # Enforce non error exit in order that validator report always goes to
        # the stdout so we can capture it
        if "--exit-zero-always" not in tool_options:
            tool_options["--exit-zero-always"] = None

        # Define default user-agent
        if "--user-agent" not in tool_options:
            tool_options["--user-agent"] = html_checker.USER_AGENT

        return interpreter_options, tool_options

    def parse_report(self, paths, content):
        """
        From given validator report content return an usable and normalized report.

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

        # To retain already outputed error messages for unknow paths
        already_seen_errors = []

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
                msg = "Validator report contains unknow path '{}'".format(path)
                if msg not in already_seen_errors:
                    already_seen_errors.append(msg)
                    self.log.warning(msg)

        return report

    def validate(self, paths, interpreter_options=None,
                 tool_options=None):
        """
        Perform validation with validator tool for given path.

        Arguments:
            paths (list): List of page path to validate.

        Keyword Arguments:
            interpreter_options (dict): Ordered dict of interpreter arguments to
                include in commandline. Default is ``None``.
            tool_options (dict): Ordered dict of validator tool arguments to
                include in commandline. Default is ``None``.

        Returns:
            collections.OrderedDict: Ordered dictionnary of checked pages from
            given path.
        """
        interpreter_options, tool_options = self.manage_options(
            interpreter_options,
            tool_options
        )

        # Build command line from options
        command = self.get_validator_command(
            paths,
            interpreter_options=interpreter_options,
            tool_options=tool_options
        )

        # Execute command process
        content = self.execute_validator(command)

        return self.parse_report(paths, content)
