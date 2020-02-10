"""
Extra Jinja template filters
"""
from pygments import highlight
from pygments.lexers import HtmlLexer
from pygments.formatters import HtmlFormatter


def highlight_html_filter(source, linenos=False, linenostart=1, identifier=None):
    """
    Filter function to highlight HTML source with Pygments and some options.

    Line breaks are replaced with character ``↩`` to improve readability.

    This does not embed Pygments styles as inline styles, you will need to
    load these stylesheets from your document.

    Example:
        {{ "<p>Foobar</p>"|highlight_html }}
        {{ "<p>Foobar</p>"|highlight_html(linenos=True) }}
        {{ "<p>Foobar</p>"|highlight_html(linenos=True, linenostart=42) }}
        {{ "<p>Foobar</p>"|highlight_html(linenos=True, identifier="foo") }}

    Arguments:
        source (string): Source string to highlight.

    Keyword Arguments:
        linenos (bool): To enable or disable line numbers. Disabled by default.
        linenostart (int): To start line numbers from a specific number.
            Default to 1.
        identifier (string): An identifier string to prefix line anchors. So
            with ``id="foo"``, line 42 anchor will be named ``foo-42``. You
            must fill it to enable line anchor.

    Returns:
        string: HTML for highlighted source.
    """
    if linenos:
        linenos = "table"

    opts = {
        "cssclass": "highlight",
        "linenos": linenos,
        "linenostart": linenostart,
        "wrapcode": True,
    }
    if linenos and identifier:
        opts.update({
            "lineanchors": identifier,
            "anchorlinenos": True,
        })

    return highlight(
        source,
        HtmlLexer(),
        HtmlFormatter(**opts)
    )
