from shutil import which

import click

from .. import __version__, __pkgname__
from ..utils.commands import get_vnu_version


@click.command()
@click.pass_context
def version_command(context):
    """
    Print out version information.
    """
    click.echo("{} {}".format(__pkgname__, __version__))

    java = which("java")
    if java:
        click.echo("└── Java found at: {}".format(java))
        vnu = get_vnu_version()
        click.echo("└── Nu Html Checker (v.Nu) {}".format(vnu))
    else:
        click.echo("└── Unable to find Java binary on your system.")
