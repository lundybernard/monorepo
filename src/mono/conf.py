from dataclasses import dataclass
from os import environ
from typing import TYPE_CHECKING

from batconf.manager import ConfigProtocol, Configuration
from batconf.source import SourceInterface, SourceList
from batconf.sources.argparse import Namespace, NamespaceConfig
from batconf.sources.env import EnvConfig
from batconf.sources.ini import IniConfig
from mono_core.database import DatabaseClient
from mono_one.conf import MonoOneConfigSchema

if TYPE_CHECKING:
    from collections.abc import Sequence


# === Configuration Schema === #
@dataclass
class MonoConfigSchema:
    name: str
    databaseA: DatabaseClient.Config  # noqa: N815
    databaseB: DatabaseClient.Config  # noqa: N815
    mono_one: MonoOneConfigSchema


"""
Use of a default configuration file location bears some careful consideration
Think carefully about the location of a default ~/.cfg/yourapp/ /etc/yourapp/ ?
  On Linux systems you may want both system and user config files.
  Windows has its own concept of appdata to conform to.
Your choice in configuration file location is entirely up to you,
  and may depend heavily on your application's needs.
"""

# Load the config file from the current working directory
CONFIG_FILE_NAME = "config.ini"


def get_config(
    config_class: ConfigProtocol = MonoConfigSchema,
    cfg_path: str = "mono",
    cli_args: Namespace | None = None,
    config_file_name: str = CONFIG_FILE_NAME,
    config_env: str | None = None,
) -> Configuration:
    """
    Build and return a configuration object for the ``mono`` namespace.

    Configuration values are resolved in priority order from:

    1. CLI arguments
    2. Environment variables
    3. INI configuration file
    4. Dataclass defaults

    If ``config_env`` is not provided, the value of ``BATCONF_ENV`` is used
    as the configuration-file environment selector.

    Args:
        config_class: Configuration schema used to define available settings.
        cfg_path: Namespace path used to resolve values for this package.
        cli_args: Optional argparse namespace containing CLI overrides.
        config_file: Optional prebuilt configuration source. If provided, it is
            used instead of creating an ``IniConfig`` from ``config_file_name``.
        config_file_name: INI file to load when ``config_file`` is not provided.
        config_env: Optional configuration-file environment name, such as
            ``"dev"`` or ``"test"``.

    Returns:
        A ``Configuration`` instance for the requested schema and namespace.
    """

    env = config_env or environ.get("BATCONF_ENV", None)

    # Build a prioritized config source list
    config_sources: Sequence[SourceInterface | None] = [
        NamespaceConfig(cli_args) if cli_args else None,
        EnvConfig(),
        IniConfig(config_file_name, config_env=env),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class, path=cfg_path)
