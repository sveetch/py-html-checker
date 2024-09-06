"""
Pytest fixtures
"""
from pathlib import Path

import pytest

import html_checker


class FixturesSettingsTestMixin(object):
    """
    A mixin containing settings about application. This is almost about useful
    paths which may be used in tests.

    Attributes:
        application_path (pathlib.Path): Absolute path to the application directory.
        package_path (pathlib.Path): Absolute path to the package directory.
        tests_dir (pathlib.Path): Directory name which include tests.
        tests_path (pathlib.Path): Absolute path to the tests directory.
        fixtures_dir (pathlib.Path): Directory name which include tests datas.
        fixtures_path (pathlib.Path): Absolute path to the tests datas.
    """
    def __init__(self):
        self.application_path = Path(html_checker.__file__).parents[0].resolve()

        self.package_path = self.application_path.parent

        self.tests_dir = "tests"
        self.tests_path = self.package_path / self.tests_dir

        self.fixtures_dir = "data_fixtures"
        self.fixtures_path = self.tests_path / self.fixtures_dir

    def format(self, content, extra=None):
        """
        Format given string to include some values related to this application.

        Arguments:
            content (str): Content string to format with possible values.

        Returns:
            str: Given string formatted with possible values.
        """
        extra = extra or {}
        return content.format(
            HOMEDIR=Path.home(),
            PACKAGE=str(self.package_path),
            APPLICATION=str(self.application_path),
            TESTS=str(self.tests_path),
            FIXTURES=str(self.fixtures_path),
            VERSION=html_checker.__version__,
            USER_AGENT=html_checker.USER_AGENT,
            **extra
        )


@pytest.fixture(scope="session")
def temp_builds_dir(tmpdir_factory):
    """Prepare a temporary build directory"""
    fn = tmpdir_factory.mktemp("builds")
    return fn


@pytest.fixture(scope="module")
def settings():
    """Initialize and return settings (mostly paths) for fixtures"""
    return FixturesSettingsTestMixin()


@pytest.fixture(scope="module")
def filter_export_payload():
    """
    Return a function to filter out items which are not computed datas
    from a given export payload.

    Arguments:
        payload (dict): Payload from exporter.

    Keyword Arguments:
        keep (list): List of top level item names to keep. Default only keep
            the "reports" and "statistics" items.
    """
    def internal_filter(payload, keep=["reports", "statistics"]):
        for key in list(payload.keys()):
            if key not in keep:
                del payload[key]

        return payload

    return internal_filter
