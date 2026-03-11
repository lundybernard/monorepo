from typing import Any, Sequence

from os import path

from batconf.manager import Configuration, ConfigProtocol

from batconf.source import SourceList, SourceInterface
from batconf.sources.argparse import NamespaceConfig, Namespace

# from batconf.sources.args import CliArgsConfig, Namespace
from batconf.sources.env import EnvConfig
from batconf.sources.ini import IniConfig


# === Configuration Schema === #
from dataclasses import dataclass
from mono_core.database import DatabaseClient
from mono_one.conf import MonoOneConfigSchema


@dataclass
class MonoConfigSchema:
    name: str
    databaseA: DatabaseClient.Config
    databaseB: DatabaseClient.Config
    mono_one: MonoOneConfigSchema


@dataclass
class RootConfigSchema:
    mono: MonoConfigSchema
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
# get config file from current working directory
CONFIG_FILE_NAME = "config.ini"


def get_config(
    config_class: ConfigProtocol | Any = MonoConfigSchema,
    cfg_path: str = "mono",
    cli_args: Namespace | None = None,
    config_file: SourceInterface | None = None,
    config_file_name: str = CONFIG_FILE_NAME,
    config_env: str | None = None,
) -> Configuration:
    """Example get_config function

    This function builds a :class:`SouceList`, which defines the configuration
    sources and lookup order.

    :param config_class: python builtin dataclass
    of type dataclass[dataclass | str].
    Type-hint includes :class:`Any` because mypy does not currently recognize
    the dataclass produced by @dataclass as satisfying the ConfigProtocol.
    :param cli_args: :class:`Namespace` provided by python's builtin argparse
    :param config_file:
    :param config_file_name:
    :param config_env: Environment id string, ex: 'dev', 'staging', 'yourname'
    used by some sources such as :class:`YamlConfig` to
    :return: A batconf :class:`Configuration` instance, used to access config
    values from the :class:`SourceList` using the config_class tree
    or module namespace (these should™ match).
    """

    # Build a prioritized config source list
    config_sources: Sequence[SourceInterface | None] = [
        NamespaceConfig(cli_args) if cli_args else None,
        EnvConfig(),
        (config_file if config_file else IniConfig(config_file_name, config_env=config_env)),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class, path=cfg_path)


CFG = get_config()
ROOT_CFG = get_config(RootConfigSchema, cfg_path=None)


def set_cli_args(args: Namespace):
    CFG._config_sources._sources.insert(0, NamespaceConfig(args))
    ROOT_CFG._config_sources._sources.insert(0, NamespaceConfig(args))
