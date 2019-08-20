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
        Format given string to include various path related to this application
        """
        return path.format(
            PACKAGE=self.package_path,
            APPLICATION=self.application_path,
            TESTS=self.tests_path,
            FIXTURES=self.fixtures_path,
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
