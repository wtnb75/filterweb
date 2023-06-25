import click
import yaml
from logging import basicConfig


@click.version_option(version="0.1", prog_name="filterweb")
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command("input")
@click.argument("name", type=str)
@click.argument("config", type=click.File("r"))
def input_test(name, config):
    from .index import open_input
    conf = yaml.safe_load(config)
    ifp = open_input(name, conf)
    click.echo(ifp.process())


@cli.command("filter")
@click.argument("name", type=str)
@click.argument("config", type=click.File("r"))
@click.argument("arg", type=click.File("r"))
def filter_test(name, config, arg):
    from .index import open_filter
    conf = yaml.safe_load(config)
    argdata = yaml.safe_load(arg)
    ifp = open_filter(name, conf)
    click.echo(ifp.apply(argdata))


@cli.command("server")
@click.argument("name", type=str)
@click.argument("config", type=click.File("r"))
@click.option("--verbose/--quiet")
def server_test(name, config, verbose):
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    if verbose:
        basicConfig(level="DEBUG", format=fmt)
    elif verbose is None:
        basicConfig(level="INFO", format=fmt)
    else:
        basicConfig(level="WARNING", format=fmt)
    from .index import open_serve
    conf = yaml.safe_load(config)
    ifp = open_serve(name, conf)
    ifp.serve()


if __name__ == "__main__":
    cli()
