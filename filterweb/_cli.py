import functools
from typing import Optional
import click
import yaml
from ._version import VERSION
from logging import getLogger

_log = getLogger(__name__)


def set_verbose(verbose: Optional[bool]):
    from logging import basicConfig

    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    if verbose:
        basicConfig(level="DEBUG", format=fmt)
    elif verbose is None:
        basicConfig(level="INFO", format=fmt)
    else:
        basicConfig(level="WARNING", format=fmt)


def verbose_option(func):
    @functools.wraps(func)
    def wrap(verbose, *args, **kwargs):
        set_verbose(verbose)
        return func(*args, **kwargs)

    return click.option("--verbose/--quiet")(wrap)


def config_arg(func):
    @functools.wraps(func)
    def wrap(config, *args, **kwargs):
        conf = yaml.safe_load(config)
        return func(*args, config=conf, **kwargs)

    return click.argument("config", type=click.File("r"))(wrap)


@click.version_option(version=VERSION, prog_name="filterweb")
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command("input")
@click.argument("name", type=str)
@config_arg
@verbose_option
def input_test(name, config):
    from .index import open_input

    ifp = open_input(name, config)
    click.echo(ifp.process())


@cli.command("filter")
@click.argument("name", type=str)
@config_arg
@click.argument("arg", type=click.File("r"))
@verbose_option
def filter_test(name, config, arg):
    from .index import open_filter

    argdata = yaml.safe_load(arg)
    ifp = open_filter(name, config)
    click.echo(ifp.apply(argdata))


@cli.command("server")
@click.argument("name", type=str)
@config_arg
@verbose_option
def server_test(name, config):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(tracer_provider=tracer_provider)
        _log.info("tracer loaded provider=%s", trace.get_tracer_provider())
    except ImportError:
        _log.info("tracer cannot loaded")
        pass

    from .index import open_serve

    ifp = open_serve(name, config)
    ifp.serve()


if __name__ == "__main__":
    cli()
