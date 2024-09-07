"""Python wrapper around library Nu Html Checker (v.Nu)"""
from importlib.metadata import version


__pkgname__ = "py-html-checker"
__version__ = version(__pkgname__)
USER_AGENT = "Validator.nu/LV py-html-checker/{}".format(__version__)
DEFAULT_INTERPRETER = "java"
DEFAULT_VALIDATOR = "{HTML_CHECKER}/vnujar/vnu.jar"
