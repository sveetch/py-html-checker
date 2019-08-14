# -*- coding: utf-8 -*-
from shutil import which

import click

from html_checker import __version__


@click.command()
@click.pass_context
def version_command(context):
    """
    Print out version information.
    """
    click.echo("py-html-checker {}".format(__version__))

    java = which("java")
    if java:
        click.echo("└── Java found at: {}".format(java))
    else:
        click.echo("└── Unable to find Java binary on your system.")
