"""
Some fixture methods
"""
import os
import pytest

import html_checker


class FixturesSettingsTestMixin(object):
    """Mixin containing some basic settings"""
    def __init__(self):
        # Base fixture datas directory
        self.application_path = os.path.abspath(os.path.dirname(html_checker.__file__))
        self.package_path = os.path.normpath(
            os.path.join(
                os.path.abspath(os.path.dirname(html_checker.__file__)),
                '..',
            )
        )
        self.tests_dir = 'tests'
        self.tests_path = os.path.join(
            self.package_path,
            self.tests_dir,
        )
        self.fixtures_dir = 'data_fixtures'
        self.fixtures_path = os.path.join(
            self.tests_path,
            self.fixtures_dir
        )

    def format(self, path):
        """
        Format given string to include various variables related to this
        application, mostly paths.
        """
        return path.format(
            HOMEDIR=os.path.expanduser("~"),
            PACKAGE=self.package_path,
            APPLICATION=self.application_path,
            TESTS=self.tests_path,
            FIXTURES=self.fixtures_path,
            VERSION=html_checker.__version__,
            USER_AGENT=html_checker.USER_AGENT,
        )


@pytest.fixture(scope='session')
def temp_builds_dir(tmpdir_factory):
    """Prepare a temporary build directory"""
    fn = tmpdir_factory.mktemp('builds')
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
