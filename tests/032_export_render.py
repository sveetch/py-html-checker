import pytest

from collections import OrderedDict

from html_checker.export.render import ExporterRenderer
from html_checker.reporter import ReportStore


@pytest.mark.parametrize("row,expected", [
    (
        {
            "type": "info",
            "message": "This is an info.",
        },
        {
            "type": "info",
            "source": {},
            "message": "This is an info."
        },
    ),
    (
        {
            "type": "error",
            "message": "This\nis\ran\terror.",
            "extract": "<some html>",
        },
        {
            "type": "error",
            "source": {
                "extract": "<some html>",
            },
            "message": "This\nis\ran\terror."
        },
    ),
    (
        {
            "type": "info",
            "subType": "warning",
            "message": "This is a warning.",
        },
        {
            "type": "warning",
            "source": {},
            "message": "This is a warning.",
        },
    ),
    (
        {
            "type": "error",
            "firstLine": 10,
            "lastLine": 20,
            "firstColumn": 1,
            "lastColumn": 2,
            "message": "This\nis\ran\terror.",
            "extract": "<some html>",
        },
        {
            "type": "error",
            "source": {
                "linestart": 10,
                "colstart": 1,
                "colend": 2,
                "extract": "<some html>",
                "lineend": 20
            },
            "message": "This\nis\ran\terror."
        },
    ),
    (
        {
            "type": "error",
            "firstLine": 10,
            "lastLine": 20,
            "firstColumn": 1,
            "lastColumn": 2,
            "message": "This\nis\ran\terror.",
        },
        {
            "type": "error",
            "source": {
                "linestart": 10,
                "colstart": 1,
                "colend": 2,
                "extract": None,
                "lineend": 20
            },
            "message": "This\nis\ran\terror."
        },
    ),
])
def test_format_row(row, expected):
    """
    Method should return a correctly formated context of message row.
    """
    exporter = ExporterRenderer()

    result = exporter.format_row("dummy.html", row)

    assert expected == result


@pytest.mark.parametrize("report,expected", [
    # Basic sample
    (
        [
            ("/html/foo.html", [
                {
                    "type": "info",
                    "message": "This is an info.",
                },
            ]),
        ],
        {
            "reports": [
                (
                    "/html/foo.html",
                    {
                        "statistics": {
                            "debugs": 0,
                            "errors": 0,
                            "infos": 1,
                            "warnings": 0,
                        },
                        "messages": [
                            {
                                "source": {},
                                "type": "info",
                                "message": "This is an info."
                            }
                        ]
                    }
                ),
            ],
        },
    ),
    # Complete sample
    (
        [
            ("http://nope", None),
            ("/html/foo.html", [
                {
                    "type": "info",
                    "message": "This is an info.",
                },
            ]),
            ("/html/wrong.html", [
                {
                    "type": "error",
                    "message": "This\nis\ran\terror.",
                    "extract": "<some html>",
                },
            ]),
            ("/html/verybad.html", [
                {
                    "type": "info",
                    "subType": "warning",
                    "message": "1. This is a warning.",
                },
                {
                    "type": "warning",
                    "message": (
                        "2. This is a warning which should never occurs from vnu."
                    ),
                },
                {
                    "type": "error",
                    "message": "3. This is a basic error.",
                },
                {
                    "type": "error",
                    "firstLine": 10,
                    "lastLine": 20,
                    "firstColumn": 1,
                    "lastColumn": 2,
                    "message": "4. This\nis\ran\terror.",
                    "extract": "<some html>",
                },
            ]),
        ],
        {
            "reports": [
                (
                    "http://nope",
                    {
                        "messages": [{
                            "message": "There was not any log report for this path.",
                            "type": "debug"
                        }],
                        "statistics": {
                            "errors": 0,
                            "infos": 0,
                            "debugs": 1,
                            "warnings": 0
                        }
                    }
                ),
                (
                    "/html/foo.html",
                    {
                        "messages": [
                            {
                                "message": "This is an info.",
                                "type": "info",
                                "source": {}
                            }
                        ],
                        "statistics": {
                            "errors": 0,
                            "infos": 1,
                            "debugs": 0,
                            "warnings": 0
                        }
                    }
                ),
                (
                    "/html/wrong.html",
                    {
                        "messages": [
                            {
                                "message": "This\nis\ran\terror.",
                                "type": "error",
                                "source": {
                                    "extract": "<some html>"
                                }
                            }
                        ],
                        "statistics": {
                            "errors": 1,
                            "infos": 0,
                            "debugs": 0,
                            "warnings": 0
                        }
                    }
                ),
                (
                    "/html/verybad.html",
                    {
                        "messages": [
                            {
                                "message": "1. This is a warning.",
                                "type": "warning",
                                "source": {}
                            },
                            {
                                "message": (
                                    "2. This is a warning which should never occurs "
                                    "from vnu."
                                ),
                                "type": "warning",
                                "source": {}
                            },
                            {
                                "message": "3. This is a basic error.",
                                "type": "error",
                                "source": {}
                            },
                            {
                                "message": "4. This\nis\ran\terror.",
                                "type": "error",
                                "source": {
                                    "linestart": 10,
                                    "lineend": 20,
                                    "extract": "<some html>",
                                    "colstart": 1,
                                    "colend": 2
                                }
                            }
                        ],
                        "statistics": {
                            "errors": 2,
                            "infos": 0,
                            "debugs": 0,
                            "warnings": 2
                        }
                    }
                ),
            ],
        },
    ),
])
def test_build(filter_export_payload, report, expected):
    """
    Method should update ``ExporterRenderer.store`` with path
    validation datas.
    """
    exporter = ExporterRenderer()

    # Directly fill report registry
    r = ReportStore([])
    r.registry = OrderedDict(report)

    exporter.build(r.registry)

    # Assertion is done on context with only the "reports" item
    assert expected == filter_export_payload(exporter.store,
                                             keep=["reports"])


def test_build_many(filter_export_payload):
    """
    Successive usage of ``build`` should add them all to render context
    without any lost and global statistics should be correctly computed from
    all data.
    """
    # Each report to build
    report_1 = [
        ("/html/foo.html", [
            {
                "type": "info",
                "message": "This is an info.",
            },
        ]),
    ]
    report_2 = [
        ("/html/bar.html", [
            {
                "type": "info",
                "subType": "warning",
                "message": "This is a warning.",
            },
        ]),
    ]
    report_3 = [
        ("http://ping", [
            {
                "type": "info",
                "subType": "warning",
                "message": "This is a warning.",
            },
            {
                "type": "info",
                "message": "This is an info.",
            },
            {
                "type": "error",
                "firstLine": 10,
                "lastLine": 20,
                "firstColumn": 1,
                "lastColumn": 2,
                "message": "4. This\nis\ran\terror.",
                "extract": "<some html>",
            },
            {
                "message": "This\nis\ran\terror.",
                "type": "error",
                "source": {
                    "extract": "<some html>"
                }
            },
        ]),
    ]

    # Expected export datas with all builded reports
    expected = {
        "reports": [
            (
                "/html/foo.html",
                {
                    "statistics": {
                        "errors": 0,
                        "warnings": 0,
                        "debugs": 0,
                        "infos": 1
                    },
                    "messages": [
                        {
                            "source": {},
                            "message": "This is an info.",
                            "type": "info"
                        }
                    ]
                }
            ),
            (
                "/html/bar.html",
                {
                    "statistics": {
                        "errors": 0,
                        "warnings": 1,
                        "debugs": 0,
                        "infos": 0
                    },
                    "messages": [
                        {
                            "source": {},
                            "message": "This is a warning.",
                            "type": "warning"
                        }
                    ]
                }
            ),
            (
                "http://ping",
                {
                    "statistics": {
                        "errors": 2,
                        "warnings": 1,
                        "debugs": 0,
                        "infos": 1
                    },
                    "messages": [
                        {
                            "source": {},
                            "message": "This is a warning.",
                            "type": "warning"
                        },
                        {
                            "source": {},
                            "message": "This is an info.",
                            "type": "info"
                        },
                        {
                            "message": "4. This\nis\ran\terror.",
                            "source": {
                                "linestart": 10,
                                "lineend": 20,
                                "extract": "<some html>",
                                "colend": 2,
                                "colstart": 1
                            },
                            "type": "error"
                        },
                        {
                            "message": "This\nis\ran\terror.",
                            "source": {},
                            "type": "error"
                        },
                    ]
                }
            ),
        ],
    }

    exporter = ExporterRenderer()

    # Directly fill report registry
    for report in [report_1, report_2, report_3]:
        r = ReportStore([])
        r.registry = OrderedDict(report)
        exporter.build(r.registry)

    assert expected == filter_export_payload(exporter.store)


def test_modelize_summary():
    """
    Report document should be correctly modelized from given report
    """
    reports = [
        (
            "/html/foo.html",
            {
                "messages": [
                    "ping",
                    "pong",
                ],
                "statistics": {"foo": 1, "bar": 1},
                "dummyvar": ["michou"],
            }
        ),
        (
            "/html/bar.html",
            {
                "messages": [
                    "pang",
                    "pung",
                ],
                "statistics": {"foo": 0, "bar": 1},
                "dummyvar": ["dumdum"],
            }
        ),
    ]

    expected = {
        "document": "foo.html",
        "context": {
            "kind": "summary",
            "metas": {
                "pac": "man",
            },
            "statistics": {
                "foo": 1,
                "bar": 2
            },
            "paths": [
                {
                    "name": "/html/foo.html",
                    "path": "path-1.txt",
                    "statistics": {
                        "foo": 1,
                        "bar": 1
                    },
                },
                {
                    "name": "/html/bar.html",
                    "path": "path-2.txt",
                    "statistics": {
                        "foo": 0,
                        "bar": 1
                    },
                }
            ]
        }
    }

    exporter = ExporterRenderer()

    doc = exporter.modelize_summary("foo.html", reports, {"pac": "man"})

    assert doc == expected


def test_modelize_report():
    """
    Report document should be correctly modelized from given report
    """
    report = (
        "/html/foo.html",
        {
            "messages": [
                "ping",
                "pong",
            ],
            "statistics": {"foo": 1, "bar": 1},
            "dummyvar": ["michou"],
        }
    )

    expected = {
        "document": "foo.html",
        "context": {
            "name": "/html/foo.html",
            "kind": "report",
            "metas": {
                "pac": "man",
            },
            "statistics": {
                "bar": 1,
                "foo": 1
            },
            "data": {
                "messages": [
                    "ping",
                    "pong"
                ],
                "dummyvar": ["michou"],
            },
        },
    }

    exporter = ExporterRenderer()

    doc = exporter.modelize_report("foo.html", report, {"pac": "man"})

    assert doc == expected


def test_modelize_audit():
    """
    Audit document should be correctly modelized from given reports
    """
    reports = [
        (
            "/html/foo.html",
            {
                "messages": [
                    "ping",
                    "pong",
                ],
                "statistics": {"foo": 1, "bar": 1},
                "dummyvar": ["michou"],
            }
        ),
        (
            "/html/bar.html",
            {
                "messages": [
                    "pang",
                    "pung",
                ],
                "statistics": {"foo": 0, "bar": 1},
                "dummyvar": ["dumdum"],
            }
        ),
    ]

    expected = {
        "document": "foo.html",
        "context": {
            "data": None,
            "kind": "audit",
            "metas": {
                "pac": "man",
            },
            "statistics": {
                "foo": 1,
                "bar": 2
            },
            "paths": [
                {
                    "name": "/html/foo.html",
                    "statistics": {
                        "foo": 1,
                        "bar": 1
                    },
                    "data": {
                        "messages": [
                            "ping",
                            "pong"
                        ],
                        "dummyvar": [
                            "michou"
                        ]
                    },
                },
                {
                    "name": "/html/bar.html",
                    "statistics": {
                        "foo": 0,
                        "bar": 1
                    },
                    "data": {
                        "messages": [
                            "pang",
                            "pung"
                        ],
                        "dummyvar": [
                            "dumdum"
                        ]
                    },
                }
            ],
        },
    }

    exporter = ExporterRenderer()

    doc = exporter.modelize_audit("foo.html", reports, {"pac": "man"})

    assert doc == expected


@pytest.mark.parametrize("pack,expected", [
    (
        True,
        [
            {
                "document": "audit.txt",
                "context": {
                    "kind": "audit",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "toast": 3,
                        "foo": 1,
                        "ping": 1,
                        "nope": 0,
                        "bar": 1
                    },
                    "data": None,
                    "paths": [
                        {
                            "name": "/html/foo.html",
                            "data": {
                                "messages": "Dummy foo"
                            },
                            "statistics": {
                                "toast": 1,
                                "foo": 1,
                                "nope": 0,
                            },
                        },
                        {
                            "name": "/html/bar.html",
                            "data": {
                                "messages": "Dummy bar"
                            },
                            "statistics": {
                                "toast": 1,
                                "bar": 1,
                                "nope": 0,
                            },
                        },
                        {
                            "name": "http://ping",
                            "data": {
                                "messages": "Dummy ping"
                            },
                            "statistics": {
                                "toast": 1,
                                "ping": 1,
                                "nope": 0,
                            },
                        }
                    ],
                },
            }
        ],
    ),
    (
        False,
        [
            {
                "document": "path-1.txt",
                "context": {
                    "name": "/html/foo.html",
                    "kind": "report",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "foo": 1,
                        "toast": 1,
                        "nope": 0
                    },
                    "data": {
                        "messages": "Dummy foo"
                    }
                }
            },
            {
                "document": "path-2.txt",
                "context": {
                    "name": "/html/bar.html",
                    "kind": "report",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "bar": 1,
                        "nope": 0,
                        "toast": 1
                    },
                    "data": {
                        "messages": "Dummy bar"
                    }
                }
            },
            {
                "document": "path-3.txt",
                "context": {
                    "name": "http://ping",
                    "kind": "report",
                    "metas": {
                        "pac": "man",
                    },
                    "statistics": {
                        "nope": 0,
                        "toast": 1,
                        "ping": 1
                    },
                    "data": {
                        "messages": "Dummy ping"
                    }
                }
            },
            {
                "document": "summary.txt",
                "context": {
                    "kind": "summary",
                    "metas": {
                        "pac": "man",
                    },
                    "paths": [
                        {
                            "path": "path-1.txt",
                            "name": "/html/foo.html",
                            "statistics": {
                                "foo": 1,
                                "toast": 1,
                                "nope": 0
                            },
                        },
                        {
                            "path": "path-2.txt",
                            "name": "/html/bar.html",
                            "statistics": {
                                "bar": 1,
                                "nope": 0,
                                "toast": 1
                            },
                        },
                        {
                            "path": "path-3.txt",
                            "name": "http://ping",
                            "statistics": {
                                "nope": 0,
                                "toast": 1,
                                "ping": 1
                            },
                        }
                    ],
                    "statistics": {
                        "bar": 1,
                        "foo": 1,
                        "ping": 1,
                        "toast": 3,
                        "nope": 0
                    },
                }
            }
        ],
    ),
])
def test_release(pack, expected):
    """
    In single release mode, only one document with all reports should be
    returned.

    In multiple files mode, there should be a document for each path report
    and an index of all documents.
    """
    exporter = ExporterRenderer()

    # Dummy store payload
    exporter.store = {
        "metas": {
            "pac": "man",
        },
        "reports": [
            (
                "/html/foo.html",
                {
                    "statistics": {
                        "toast": 1,
                        "foo": 1,
                        "nope": 0,
                    },
                    "messages": "Dummy foo",
                }
            ),
            (
                "/html/bar.html",
                {
                    "statistics": {
                        "toast": 1,
                        "bar": 1,
                        "nope": 0,
                    },
                    "messages": "Dummy bar",
                }
            ),
            (
                "http://ping",
                {
                    "statistics": {
                        "toast": 1,
                        "ping": 1,
                        "nope": 0,
                    },
                    "messages": "Dummy ping",
                }
            ),
        ],
        "statistics": {}
    }

    results = exporter.release(pack=pack)

    assert results == expected
