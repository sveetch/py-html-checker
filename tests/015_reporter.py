import os
from collections import OrderedDict

import pytest

from html_checker.exceptions import ReportError
from html_checker.reporter import ReportStore


@pytest.mark.parametrize("paths,expected", [
    # Url path
    (
        [
            "http://perdu.com",
        ],
        [
            ("http://perdu.com", None),
        ],
    ),
    # Unexisting file path
    (
        [
            "nope.html",
        ],
        [
            ("nope.html", [{
                "type": "critical",
                "message": "File path does not exists."
            }]),
        ],
    ),
    # Unexisting absolute file path
    (
        [
            "{FIXTURES}/nope.html",
        ],
        [
            ("{FIXTURES}/nope.html", [{
                "type": "critical",
                "message": "File path does not exists."
            }]),
        ],
    ),
    # Relative file path
    (
        [
            "tests/data_fixtures/html/valid.basic.html",
        ],
        [
            ("{FIXTURES}/html/valid.basic.html", None),
        ],
    ),
    # Absolute file path
    (
        [
            "{FIXTURES}/html/valid.basic.html",
        ],
        [
            ("{FIXTURES}/html/valid.basic.html", None),
        ],
    ),
])
def test_initial_registry(settings, paths, expected):
    """
    Should build a correct registry of initial values for required path.
    """
    r = ReportStore([])

    paths = [settings.format(item) for item in paths]

    expected = [(settings.format(k), v) for k, v in expected]

    assert expected == r.initial_registry(paths)


@pytest.mark.parametrize("content,expected", [
    (
        b"{}",
        "Invalid JSON report: it must contains a 'messages' item of checked page list.",
    ),
    (
        b"{",
        "Invalid JSON report: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
    ),
])
def test_parse_invalid(content, expected):
    """
    Parse should raise an exception when given content is invalid.
    """
    r = ReportStore([])

    with pytest.raises(ReportError) as excinfo:
        r.parse(content)

    #print(str(excinfo.value))

    assert expected == str(excinfo.value)


@pytest.mark.parametrize("content,expected", [
    (
        b'{"messages": "foo"}',
        {"messages": "foo"},
    ),
    (
        b'  {"messages": "foo", "ping": "pong"}  ',
        {"messages": "foo", "ping": "pong"},
    ),
])
def test_parse_success(content, expected):
    """
    Parse should return a Python object from valid content.
    """
    r = ReportStore([])

    assert expected == r.parse(content)


@pytest.mark.parametrize("paths,contents,expected", [
    (
        ["foo.html"],
        [
            b"""{"messages":[]}""",
        ],
        [
            ("foo.html", [
                {
                    "type": "critical",
                    "message": "File path does not exists."
                },
            ])
        ]
    ),
    (
        ["foo.html"],
        [
            b"""{"messages":[{"url": "http://perdu.com"}]}""",
        ],
        [
            ("foo.html", [
                {
                    "type": "critical",
                    "message": "File path does not exists."
                },
            ]),
        ]
    ),
    (
        ["foo.html", "http://perdu.com"],
        [
            b"""{"messages":[]}""",
        ],
        [
            ("foo.html", [
                {
                    "type": "critical",
                    "message": "File path does not exists."
                },
            ]),
            ("http://perdu.com", None),
        ]
    ),
    (
        ["foo.html", "http://perdu.com"],
        [
            b"""{"messages":[{"url": "foo.html"}]}""",
            b"""{"messages":[{"url": "http://perdu.com", "ping": "pong"}]}""",
            b"""{"messages":[{"url": "http://perdu.com", "pif": "paf"}]}""",
        ],
        [
            ("foo.html", [
                {
                    "type": "critical",
                    "message": "File path does not exists."
                },
                {},
            ]),
            ("http://perdu.com", [
                {"ping": "pong"},
                {"pif": "paf"},
            ])
        ]
    ),
])
def test_add(paths, contents, expected):
    """
    Given valid contents should be validated and added to registry.
    """
    r = ReportStore(paths)

    for content in contents:
        r.add(content)

    assert OrderedDict(expected) == r.registry
