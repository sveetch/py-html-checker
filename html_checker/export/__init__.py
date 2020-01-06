from .logs import LoggingExport

from html_checker.exceptions import ExportError

# We do not expose base exporters which have no specific format and able to
# build something concrete
__all__ = [
    "LoggingExport",
]


EXPORTER_CHOICES = ["logging"]


# Enable HTML format if Jinja is installed
try:
    import jinja2
except ImportError:
    pass
else:
    from .jinja import JinjaExport
    EXPORTER_CHOICES.append("html")
    __all__.append("JinjaExport")


def get_exporter(name):
    """
    Select the exporter class from given format name.

    Arguments:
        name (string): Format name as defined in exporter class attribute
            ``FORMAT_NAME``.

    Returns:
        object: The exporter class.
    """
    formats = {}
    for item in __all__:
        cls = globals()[item]
        formats[cls.FORMAT_NAME] = cls

    if name not in formats:
        msg = "There is no exporter with format name '{}'"
        raise ExportError(msg.format(name))

    return formats[name]