from collections.abc import Iterator
from contextlib import contextmanager
from os import environ

from mono_core.database import KEY2_DEFAULT
from pytest import raises  # noqa: PT013

from mono.conf import MonoConfigSchema, get_config


def test_get_config() -> None:
    """Bare get_config() returns a Project-level Configuration object.
    Submodule configs can be accessed using their namespace.
    """
    cfg = get_config()
    # This cfg object can be used to lookup default values
    # provided by the Config dataclasses for the module.
    assert cfg.databaseA.key2 == KEY2_DEFAULT


def test_reusable_configuration_schemas() -> None:
    """
    In this example, we demonstrate reusing the Client.Config Schema
    to provide configurations for multiple clients of the same type.
    """
    cfg = get_config(config_env="test")
    assert cfg.databaseA.key1 == "config.ini: test.mono.databaseA.key1"
    assert cfg.databaseB.key1 == "config.ini: test.mono.databaseB.key1"
    # Multiple sub-configs from the same Schema share default values
    assert cfg.databaseA.key2 == KEY2_DEFAULT
    assert cfg.databaseB.key2 == KEY2_DEFAULT


def test_environment_variable() -> None:
    """Setting an environment variable, using the project namespace

    The environment variable name is the namespace-path to the cfg key
    All Uppercase, '_'(underscore) delimited.
    """
    value = "Environment, value"
    override_value = "overwrite key2 default"

    cfg = get_config(config_class=MonoConfigSchema)

    # Environment variables overwrite defaults from the Config class
    with set_environ("MONO_DATABASEA_KEY2", override_value):
        assert cfg.databaseA.key2 == override_value

    # We have a limited ability to add new key:value pairs.
    # at this time, they must be added to existing namespaces
    with set_environ("MONO_ENVKEY", value):
        assert cfg.envkey == value

    # Unsupported arbitrary namespace
    with raises(AttributeError), set_environ("MONO_UNKNOWN_KEY", value):
        assert cfg.unknown.key == value


def test_config_env_environment_variable() -> None:
    # The config_env can be set using the environment variable BATCONF_ENV
    with set_environ("BATCONF_ENV", "test"):
        cfg = get_config(config_class=MonoConfigSchema)
        assert cfg.databaseA.key1 == "config.ini: test.mono.databaseA.key1"


@contextmanager
def set_environ(key: str, value: str) -> Iterator[None]:
    try:
        environ[key] = value
        yield
    finally:
        del environ[key]
