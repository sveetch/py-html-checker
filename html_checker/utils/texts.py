from ..exceptions import HtmlCheckerBaseException


def format_hostname(value):
    """
    Given a string value, check if it's a valid hostname. Optional port can be
    given, the host name and port have to be separated with a ``:`` like
    ``localhost:8000``.

    Arguments:
        value (string): A hostname to validate.

    Returns:
        string: Validated hostname, if port has not been given, default port
        will be ``8002``.
    """
    parts = value.split(":")
    hostname = parts[0]

    if not hostname:
        raise HtmlCheckerBaseException("Given server hostname is empty.")

    if len(parts) > 1 and parts[1]:
        port = parts[1]
        try:
            port = int(port)
        except ValueError:
            raise HtmlCheckerBaseException("Given server port number is invalid.")
    else:
        port = 8002

    return (hostname, port)
