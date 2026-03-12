# ruff: noqa: PT009, PT027, N803, N805, TID252

from configparser import ConfigParser
from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import Mock, patch

from tests.test_cli import set_environ

from ..conf import (
    Namespace,
    get_config,
)

SRC = "mono_one.conf"

EXAMPLE_confIG_INI = """
[batconf]
default_env = example

[example]
[example.mono_one]
key = value
[example.mono_one.remote_host]
api_key = example_api_key
url = https://api-example.host.io/

[alt]
[alt.mono_one]
[alt.mono_one.module]
key = alt_value
"""

CONFIG_PARSER_ENVS = ConfigParser()
CONFIG_PARSER_ENVS.read_string(EXAMPLE_confIG_INI)


class get_config_Tests(TestCase):  # noqa: N801
    IniConfig: Mock

    def setUp(t) -> None:
        patches = [
            "IniConfig",
        ]
        for target in patches:
            patcher = patch(f"{SRC}.{target}", autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t.config_file_data = {
            "default": "test_config",
            "test_config": {
                "mono_one": {
                    "AModule": {
                        "arg_1": "conf_file_arg_1",
                        "arg_2": "conf_file_arg_2",
                    },
                    "BModule": {
                        "arg_1": "2020-20-21",
                    },
                }
            },
        }

        @dataclass
        class ConfA:
            arg_1: str = "dataclass_default_arg_1"
            arg_2: str = "dataclass_default_arg_2"
            arg_3: str = "dataclass_default_arg_3"

        @dataclass
        class ConfB:
            arg_1: str = "dataclass_default_isodate"

        @dataclass
        class ConfigSchema:
            AModule: ConfA
            BModule: ConfB
            config_file: str = "./config.ini"

        t.ConfigSchema = ConfigSchema

    def test_without_parameters(t) -> None:
        _ = get_config()

    @patch(f"{SRC}.EnvConfig", autospec=True)
    def test_default_values(t, EnvConfig: Mock) -> None:
        t.IniConfig.return_value = None
        EnvConfig.return_value = None

        conf = get_config(t.ConfigSchema)

        t.assertEqual(conf.AModule.arg_3, "dataclass_default_arg_3")
        t.assertEqual(conf.BModule.arg_1, "dataclass_default_isodate")

    def test_arg_cli_args(t) -> None:
        cli_args = Namespace()
        setattr(cli_args, "mono_one.AModule.arg_1", "cli_arg_1")

        conf = get_config(t.ConfigSchema, cli_args=cli_args)
        t.assertEqual(conf.AModule.arg_1, "cli_arg_1")

    def test_arg_config_file_name(t) -> None:
        """The given config_file_name is passed to the IniConfig constructor"""
        config_file_name = "./test.config.yaml"
        get_config(t.ConfigSchema, config_file_name=config_file_name)
        t.IniConfig.assert_called_with(config_file_name, config_env=None)

    def test_arg_config_env(t) -> None:
        """The given config_env name is passed to the IniConfig constructor"""
        config_env = "configuration file environment"
        get_config(t.ConfigSchema, config_env=config_env)
        t.IniConfig.assert_called_with("config.ini", config_env=config_env)

    def test_environment_variable_config_env(t) -> None:
        """The BATconf_ENV value is used for config_env,
        it is used as a fallback value
        """
        config_env = "configuration file environment"
        with set_environ("BATconf_ENV", config_env):
            get_config(t.ConfigSchema)
            t.IniConfig.assert_called_with("config.ini", config_env=config_env)

    @patch(f"{SRC}.EnvConfig", autospec=True)
    def test__getattr__missing_attribute(t, EnvConfig: Mock) -> None:
        t.IniConfig.return_value = None
        EnvConfig.return_value = None

        conf = get_config(t.ConfigSchema)
        with t.assertRaises(AttributeError):
            _ = conf.sir_not_appearing_in_this_film
