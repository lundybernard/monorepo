"""CLI commands for mono."""

from __future__ import annotations

from argparse import Namespace

import typer
from mono_core import say_hello
from mono_one import say_hi
from mono_two import say_bye

from .conf import get_config

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
    batconf_env: str | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Config file environment",
    ),
    dbakey1: str = typer.Option(None, "--dbkey"),
) -> None:
    """Entry point for the CLI."""
    ctx.ensure_object(dict)
    args = {
        "batconf.env": batconf_env,
        "mono.name": name,
        "mono.databaseA.key1": dbakey1,
    }
    ctx.obj = args


@app.command()
def hello(
    ctx: typer.Context,
    name: str = typer.Argument(None, help="Name to greet"),
) -> None:
    """Say hello to someone (using mono_core)."""
    # mono_core.greetings.say_hello is not configurable
    # so we pass the mono-package name value to it.
    ctx.obj["mono.name"] = name
    cfg = _cfg_from_ctx(ctx)
    try:
        typer.echo(say_hello(cfg.name))
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
    # mono_one.greetings.say_hi is configurable,
    # so we can pass the CLI args to it, and it will use them.

    greeting = say_hi(
        cli_args=Namespace(**ctx.obj),
        config_env=ctx.obj["batconf.env"],
    )
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
    typer.echo(_cfg_from_ctx(ctx))


def _cfg_from_ctx(ctx: typer.Context):
    args = Namespace(**ctx.obj)
    return get_config(cli_args=args, config_env=ctx.obj["batconf.env"])
