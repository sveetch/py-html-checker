# -*- coding: utf-8 -*-
from shutil import which

import click

from html_checker import __version__
from html_checker.utils import get_vnu_version


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
        vnu = get_vnu_version()
        click.echo("└── Nu Html Checker (v.Nu) {}".format(vnu))
    else:
        click.echo("└── Unable to find Java binary on your system.")
