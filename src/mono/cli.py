"""CLI commands for mono."""

from __future__ import annotations

from argparse import Namespace  # Temp, maybe replace with Typer config source

import typer
from mono_core import say_hello
from mono_one import say_hi
from mono_two import say_bye

from .conf import set_cli_args, CFG

HELP_TEXT = """A minimal Python CLI monorepo template.

\b
Examples:
  $ mono hello World
  Hello, World!

  $ mono hi Alice
  Hi, Alice!

  $ mono bye Bob
  Goodbye, Bob!
"""

app = typer.Typer(
    help=HELP_TEXT,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    name: str = typer.Option(
        None,
        "--name",
        "-n",
        help="Name to greet",
    ),
    dbakey1: str = typer.Option(None, "--dbkey"),
) -> None:
    """Entry point for the CLI."""
    ctx.ensure_object(dict)
    ARGS = {
        "mono.name": name,
        "mono.databaseA.key1": dbakey1,
    }
    ctx.obj = ARGS
    print(f"{ARGS=}")


@app.command()
def hello(
    ctx: typer.Context,
    name: str = typer.Argument(None, help="Name to greet"),
) -> None:
    """Say hello to someone (using mono_core)."""
    # mono_core.greetings.say_hello is not configurable
    # so we pass the mono-package name value to it.
    ctx.obj["mono.name"] = name
    set_cli_args(Namespace(**ctx.obj))
    try:
        typer.echo(say_hello(CFG.name))
    except AttributeError:
        # if the name is not set by the CLI, or the configuration,
        # fall-back to the function's default
        typer.echo(say_hello())


@app.command()
def hi(
    ctx: typer.Context,
    hi_name: str = typer.Argument(None, help="Name to greet"),
    language: str = typer.Option(None, "-l", "--language"),
) -> None:
    """Say hi to someone (using mono_one)."""
    # Set mono_one package-level config values
    ctx.obj["mono_one.name"] = hi_name
    ctx.obj["mono_one.language"] = language
    set_cli_args(Namespace(**ctx.obj))
    # mono_one.greetings.say_hi is configurable,
    # so we can pass the CLI args to it, and it will use them.
    greeting = say_hi(cli_args=Namespace(**ctx.obj))
    typer.echo(greeting)


@app.command()
def bye(
    name: str = typer.Argument("Friend", help="Name to say goodbye to"),
) -> None:
    """Say goodbye to someone (using mono_two)."""
    message = say_bye(name)
    typer.echo(message)


@app.command()
def config(
    ctx: typer.Context,
    dbak2: str = typer.Option(None, "--dba-key"),
    dbbk2: str = typer.Option("CLI DEFAULT DBB KEY 2", "--dbb-key"),
) -> None:
    """Prints the current configuration, and source list.
    For demonstration purposes,
    2 of the database keys can be set using cli options
    """
    ctx.obj["mono.databaseA.key2"] = dbak2
    ctx.obj["mono.databaseB.key2"] = dbbk2
    set_cli_args(Namespace(**ctx.obj))

    # cfg = _cfg_from_ctx(ctx)
    # cfg = get_config()  # without args
    typer.echo(CFG)

    from .conf import ROOT_CFG

    typer.echo(ROOT_CFG)

    print(ROOT_CFG._config_sources._sources[2].get(key="mono_one.name"))


def _cfg_from_ctx(ctx: typer.Context):
    from .conf import get_config

    args = Namespace(**ctx.obj)
    return get_config(cli_args=args)


def apply_cli_config(ctx: typer.Context, command_values: dict) -> None:
    ctx.obj.update(command_values)
    set_cli_args(Namespace(**ctx.obj))


# def _set_args(args: Namespace):
#    from batconf.sources.argparse import NamespaceConfig
#    from .conf import CFG
#    CFG._config_sources._sources.insert(0, NamespaceConfig(args))
