from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import wraps
from os import environ
from typing import Any, Protocol, TypeVar

from batconf.manager import ConfigProtocol, Configuration
from batconf.source import SourceInterface, SourceList
from batconf.sources.argparse import Namespace, NamespaceConfig
from batconf.sources.env import EnvConfig
from batconf.sources.ini import IniConfig

# Load config.ini from the current working directory
CONFIG_FILE_NAME = "config.ini"


@dataclass
class MonoOneConfigSchema:
    name: str = "Friend"
    language: str = "english"


T_co = TypeVar("T_co", covariant=True)


class ConfigurableFunc(Protocol[T_co]):
    def __call__(
        self,
        *,
        cfg: Configuration,
        **kwargs: object,
    ) -> T_co: ...


class ConfiguredCallable[R](Protocol):
    def __call__(
        self,
        *,
        cli_args: Namespace | None = None,
        config_file_name: str = CONFIG_FILE_NAME,
        config_env: str | None = None,
        **kwargs: object,
    ) -> R: ...


def configurable[R](func: Callable[..., R]) -> ConfiguredCallable[R]:
    """Wrap a function so its defaults can be supplied from configuration.

    The wrapped function receives a ``cfg`` object built by ``get_config()``.
    Optional CLI arguments, config file name, and config environment can be
    passed through to control configuration resolution.
    """

    @wraps(func)
    def wrapper(
        *,
        cli_args: Namespace | None = None,
        config_file_name: str = CONFIG_FILE_NAME,
        config_env: str | None = None,
        **kwargs: object,
    ) -> R:
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
    config_class: ConfigProtocol | Any = MonoOneConfigSchema,
    cfg_path: str = "mono_one",
    cli_args: Namespace | None = None,
    config_file_name: str = CONFIG_FILE_NAME,
    config_env: str | None = None,
) -> Configuration:
    """Build and return a configuration object for the ``mono_one`` namespace.

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
