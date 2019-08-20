# -*- coding: utf-8 -*-
import click


@click.command()
@click.pass_context
def site_command(context):
    """
    Todo: should validate every page defined in a sitemap
    """
    click.echo("TODO 'site_command'")
