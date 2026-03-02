# === Configuration Schema === #
from collections.abc import Sequence
from dataclasses import dataclass
from os import environ

from batconf.manager import ConfigProtocol, Configuration
from batconf.source import SourceInterface, SourceList
from batconf.sources.argparse import Namespace, NamespaceConfig
from batconf.sources.env import EnvConfig
from batconf.sources.ini import IniConfig
from mono_core.database import DatabaseClient
from mono_one.conf import MonoOneConfigSchema


@dataclass
class MonoConfigSchema:
    name: str
    databaseA: DatabaseClient.Config
    databaseB: DatabaseClient.Config
    mono_one: MonoOneConfigSchema


"""
Use of a default configuration file location bears some careful consideration
Think carefully about the location of a default ~/.cfg/yourapp/ /etc/yourapp/ ?
  On Linux systems you may want both system and user config files.
  Windows has its own concept of appdata to conform to.
Your choice in configuration file location is entirely up to you,
  and may depend heavily on your application's needs.

Let us know if you would find some default settings 
based on OS standards useful.
"""

# Get the absolute path to the test config.yaml file
# _project_dir = path.dirname(path.realpath(__file__))
# CONFIG_FILE_NAME = path.join(_project_dir, '../config.ini')
# Load config file from current working directory
CONFIG_FILE_NAME = "config.ini"


def get_config(
    config_class: ConfigProtocol = MonoConfigSchema,
    cfg_path: str = "mono",
    cli_args: Namespace | None = None,
    config_file: SourceInterface | None = None,
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
        (config_file or IniConfig(config_file_name, config_env=env)),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class, path=cfg_path)
