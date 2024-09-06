import logging
import os
import pytest

import cherrypy

from html_checker.serve import ReleaseServer

from html_checker.exceptions import HTTPServerError


def mock_cherrypy_quickstart(*args, **kwargs):
    """
    Mock quickstart to do nothing.
    """
    pass


def test_notemp_mode_basedir_required():
    """
    An exception is raised if temporary mode is disabled but basedir is not
    provided.
    """
    with pytest.raises(HTTPServerError):
        ReleaseServer(**{
            "hostname": "localhost",
            "port": 8000,
            "temporary": False,
        })


def test_temp_mode_basedir_conflict():
    """
    An exception is raised if temporary mode is enabled and basedir is given
    since it has no sense.
    """
    with pytest.raises(HTTPServerError):
        ReleaseServer(**{
            "hostname": "localhost",
            "port": 8000,
            "basedir": "foobar",
            "temporary": True,
        })


def test_temp_basedir():
    """
    Base directory can be omitted in temporary mode, a temporary directory will
    be created and set as base directory
    """
    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8000,
        "temporary": True,
    })

    assert s.temporary is True
    assert os.path.exists(s.basedir) is True
    assert os.path.isdir(s.basedir) is True

    # Remove temp directory manually, we don"t want to rely on
    # "ReleaseServer.flush" yet
    os.rmdir(s.basedir)


def test_basic():
    """
    When base directory is given and temporary mode is disabled, it should work
    nicely.
    """
    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8000,
        "basedir": "/foo/bar",
        "temporary": False,
    })

    assert s.temporary is False
    assert "/foo/bar" == s.basedir


def test_temp_mode_flush():
    """
    In temporary mode, flush should recursively remove the created temporary
    directory
    """
    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8000,
        "temporary": True,
    })

    assert s.flush() == s.basedir
    assert os.path.exists(s.basedir) is False


def test_notemp_mode_flush():
    """
    If temporary mode is disabled, flush does not do anything.
    """
    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8000,
        "basedir": "/foo/bar",
        "temporary": False,
    })

    assert os.path.exists(s.basedir) is False
    assert s.flush() is None


def test_temp_mode_config():
    """
    Ensure server and app configurations are correct with enabled temporary
    mode.
    """
    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8000,
        "temporary": True,
    })
    temporary_basedir = s.basedir

    expected_server = {
        "server.socket_host": "localhost",
        "server.socket_port": 8000,
        "engine.autoreload_on": False,
    }
    assert expected_server == s.get_server_config()

    expected_app = {
        "/": {
            "tools.staticdir.index": "index.html",
            "tools.staticdir.on": True,
            "tools.staticdir.dir": temporary_basedir,
        },
    }
    assert expected_app == s.get_app_config()

    s.flush()


def test_notemp_mode_config():
    """
    Ensure server and app configurations are correct with disabled temporary
    mode.
    """
    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8000,
        "basedir": "/foo/bar",
        "temporary": False,
    })

    expected_server = {
        "server.socket_host": "localhost",
        "server.socket_port": 8000,
        "engine.autoreload_on": False,
    }
    assert expected_server == s.get_server_config()

    expected_app = {
        "/": {
            "tools.staticdir.index": "index.html",
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "/foo/bar",
        },
    }
    assert expected_app == s.get_app_config()

    s.flush()


def test_temp_mode_run(monkeypatch, caplog):
    """
    Just ensure the run() method does log information and does not break with
    temporary mode enabled.

    Mockup the cherrypy method since we don't want to test it and server config
    is basic enough to be trusted.
    """
    monkeypatch.setattr(cherrypy, "quickstart", mock_cherrypy_quickstart)

    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8000,
        "temporary": True,
    })

    with caplog.at_level(logging.DEBUG):
        s.run()

    msg_host = "Starting HTTP server on: localhost:8000"
    msg_dir = "Serving report from: {}"
    expected = [
        ("py-html-checker", logging.INFO, msg_host),
        ("py-html-checker", logging.DEBUG, msg_dir.format(s.basedir)),
        ("py-html-checker", logging.WARNING, "Use CTRL+C to terminate."),
    ]
    assert expected == caplog.record_tuples

    s.flush()


def test_notemp_mode_run(monkeypatch, caplog):
    """
    Just ensure the run() method does log information and does not break with
    temporary mode disabled.

    Mockup the cherrypy method since we don't want to test it and server config
    is basic enough to be trusted.
    """
    monkeypatch.setattr(cherrypy, "quickstart", mock_cherrypy_quickstart)

    s = ReleaseServer(**{
        "hostname": "localhost",
        "port": 8001,
        "basedir": "/foo/bar",
        "temporary": False,
    })

    with caplog.at_level(logging.DEBUG):
        s.run()

    msg_host = "Starting HTTP server on: localhost:8001"
    expected = [
        ("py-html-checker", logging.INFO, msg_host),
        ("py-html-checker", logging.DEBUG, "Serving report from: /foo/bar"),
        ("py-html-checker", logging.WARNING, "Use CTRL+C to terminate."),
    ]
    assert expected == caplog.record_tuples

    s.flush()
