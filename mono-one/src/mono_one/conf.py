from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import wraps
from typing import Any

from batconf.manager import ConfigProtocol, Configuration
from batconf.source import SourceInterface, SourceList
from batconf.sources.argparse import Namespace, NamespaceConfig
from batconf.sources.env import EnvConfig
from batconf.sources.ini import IniConfig

# Get the absolute path to the test config file relative to this file
# _project_dir = path.dirname(path.realpath(__file__))
# CONFIG_FILE_NAME = path.join(_project_dir, '../config.ini')
# get config.ini from the current working directory
CONFIG_FILE_NAME = "config.ini"


@dataclass
class MonoOneConfigSchema:
    name: str = "Friend"
    language: str = "english"


def configurable(func: Callable) -> Callable:
    """
    configurable is a decorator for library functions.
    It modifies the functon signature to accept parameters
    needed for the get_config function.
    """

    @wraps(func)
    def wrapper(
        cli_args: Namespace | None = None,
        config_file_name: str = CONFIG_FILE_NAME,
        config_env: str | None = None,
        **kwargs,
    ):
        # Fetch the configuration using get_config
        cfg = get_config(
            cli_args=cli_args,
            config_file_name=config_file_name,
            config_env=config_env,
        )
        # Pass the configuration as the first argument to the wrapped function
        return func(cfg=cfg, **kwargs)

    return wrapper


def get_config(
    config_class: ConfigProtocol = MonoOneConfigSchema,
    cfg_path: str = "mono_one",
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
        (config_file or IniConfig(config_file_name, config_env=config_env)),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class, path=cfg_path)
