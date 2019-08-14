import os
from collections import OrderedDict

import pytest

from html_checker.validator import ValidatorInterface

from html_checker.exceptions import (PathInvalidError, SitemapInvalidError,
                              ValidatorError)


@pytest.mark.parametrize("interpreter,options,expected", [
    (
        "",
        {},
        [],
    ),
    (
        None,
        {},
        ["java", "-jar"],
    ),
    (
        None,
        ["-Xss512k"],
        ["java", "-Xss512k", "-jar"],
    ),
    (
        "machin",
        {},
        ["machin"],
    ),
])
def test_get_interpreter_part(interpreter, options, expected):
    """
    Should return command for interpreter part
    """
    v = ValidatorInterface()

    if interpreter is not None:
        v.INTERPRETER = interpreter

    assert expected == v.get_interpreter_part(options=options)


@pytest.mark.parametrize("interpreter,validator,interpreter_options,tool_options,path,expected", [
    (
        None,
        None,
        [],
        [],
        "foo.html",
        ["java", "-jar", "{HTML_CHECKER}/vnujar/vnu.jar", "foo.html"],
    ),
    (
        None,
        "",
        [],
        [],
        "foo.html",
        ["java", "-jar", "foo.html"],
    ),
    (
        None,
        "dummytool",
        [],
        [],
        "foo.html",
        ["java", "-jar", "dummytool", "foo.html"],
    ),
    (
        "dummycli",
        "validate",
        ["-v", "3"],
        ["--foo", "bar"],
        "foo.html",
        ["dummycli", "-v", "3", "validate", "--foo", "bar", "foo.html"],
    ),
])
def test_get_validator_command(settings, interpreter, validator,
                               interpreter_options, tool_options, path,
                               expected):
    """
    Should return full command line to execute validator tool for given path

    To avoid hardcoding absolute path in test parameters, expected path is
    formatted with application path.
    """
    v = ValidatorInterface()

    if interpreter is not None:
        v.INTERPRETER = interpreter

    if validator is not None:
        v.VALIDATOR = validator

    expected = [item.format(HTML_CHECKER=settings.application_path) for item in expected]

    assert expected == v.get_validator_command(
        path,
        interpreter_options=interpreter_options,
        tool_options=tool_options
    )


@pytest.mark.parametrize("interpreter,validator,interpreter_options,tool_options,path,expected", [
    # Unreachable interpreter
    (
        "nietniet",
        None,
        [],
        [],
        "http://perdu.com",
        "Unable to reach interpreter to run validator: [Errno 2] No such file or directory: 'nietniet'",
    ),
    # Unreachable validator
    (
        None,
        "nietniet",
        [],
        [],
        "http://perdu.com",
        "Validator execution failed: Error: Unable to access jarfile nietniet\n",
    ),
    # Wrong option on validator (wrong option on interpreter are ignored)
    (
        None,
        None,
        ["--bizarro"],
        [],
        "http://perdu.com",
        ("Validator execution failed: Unrecognized option: --bizarro\n"
         "Error: Could not create the Java Virtual Machine.\n"
         "Error: A fatal exception has occurred. Program will exit.\n"),
    ),
])
def test_validate_fail(settings, interpreter, validator,
                       interpreter_options, tool_options, path, expected):
    """
    Exception should be raised when there is an error while executing
    interpreter or validator. Note than validator won't throw any error when
    pages to check is missing, invalid, etc..
    """
    v = ValidatorInterface()

    path = path.format(FIXTURES=settings.fixtures_path)

    if interpreter is not None:
        v.INTERPRETER = interpreter

    if validator is not None:
        v.VALIDATOR = validator

    with pytest.raises(ValidatorError) as excinfo:
        v.validate(
            path,
            interpreter_options=interpreter_options,
            tool_options=tool_options
        )

    assert expected == str(excinfo.value)


@pytest.mark.parametrize("paths,content,expected", [
    (
        ["foo.html"],
        b"""{"messages":[]}""",
        OrderedDict([("foo.html", None)])
    ),
    (
        ["foo.html"],
        b"""{"messages":[{"url": "http://perdu.com"}]}""",
        OrderedDict([("foo.html", None)])
    ),
    (
        ["foo.html", "http://perdu.com"],
        b"""{"messages":[]}""",
        OrderedDict([
            ("foo.html", None),
            ("http://perdu.com", None),
        ])
    ),
    (
        ["foo.html", "http://perdu.com"],
        b"""{"messages":[{"url": "foo.html"}, {"url": "http://perdu.com", "ping": "pong"}, {"url": "http://perdu.com", "pif": "paf"}]}""",
        OrderedDict([
            ("foo.html", [{}]),
            ("http://perdu.com", [
                {"ping": "pong"},
                {"pif": "paf"},
            ])
        ])
    ),
])
def test_parse_report(settings, paths, content, expected):
    """
    Path reports should be indexed on their path and contains their full report
    payload.
    """
    v = ValidatorInterface()

    assert expected == v.parse_report(paths, content)


@pytest.mark.parametrize("interpreter,validator,interpreter_options,tool_options,path,expected", [
    (
        None,
        None,
        [],
        [],
        "{FIXTURES}/foo.html",
        """{"messages":[]}""",
    ),
    (
        None,
        None,
        [],
        [],
        "{FIXTURES}/html/valid.basic.html",
        "plouf",
    ),
    (
        None,
        None,
        [],
        [],
        "http://perdu.com",
        "plouf",
    ),
])
def test_validate_success(settings, interpreter, validator,
                          interpreter_options, tool_options, path, expected):
    """
    Should call the validator tool to process checking on given path

    TODO: Unfinished test, it fails because:
          1. FIXTURES directory is not prepend to report path;
          2. Expected report are not populated yet with validator results;
    """
    v = ValidatorInterface()

    path = path.format(FIXTURES=settings.fixtures_path)

    if interpreter is not None:
        v.INTERPRETER = interpreter

    if validator is not None:
        v.VALIDATOR = validator

    assert expected == v.validate(
        path,
        interpreter_options=interpreter_options,
        tool_options=tool_options
    )
