"""Tests for the mono CLI tool."""

from __future__ import annotations

from contextlib import contextmanager
from os import environ

from typer.testing import CliRunner

from mono import app

runner = CliRunner()


def test_hello_command_default() -> None:
    """Test hello command with default argument."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_config_command() -> None:
    """Test config prints the current configuration settings"""
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert (
        "mono <class 'mono.conf.MonoConfigSchema'>:\n"
        '    |- name: "MISSING_VALUE"\n'
        "    |- databaseA <class 'mono_core.database.DatabaseClient.Config'>:\n"
        '    |    |- key1: "MISSING_VALUE"\n'
        '    |    |- key2: "mono_core.database: KEY2_DEFAULT"\n'
    ) in result.stdout


def test_env_argument() -> None:
    """Setting --env=test loads the test environment from the config file"""
    result = runner.invoke(app, ["--env=test", "config"])
    assert result.exit_code == 0
    assert (
        "    |- databaseA <class 'mono_core.database.DatabaseClient.Config'>:\n"
        '    |    |- key1: "config.ini: test.mono.databaseA.key1"\n'
    ) in result.stdout


def test_env_from_environment() -> None:
    """Setting BATCONF_ENV=test loads the test environment from the config file"""
    with set_environ("BATCONF_ENV", "test"):
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert (
            "    |- databaseA <class 'mono_core.database.DatabaseClient.Config'>:\n"
            '    |    |- key1: "config.ini: test.mono.databaseA.key1"\n'
        ) in result.stdout


def test_hello_command_with_name() -> None:
    """Test hello command with custom name."""
    result = runner.invoke(app, ["hello", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.stdout


def test_hello_command_with_env_variable() -> None:
    with set_environ("MONO_NAME", "Environment"):
        result = runner.invoke(app, ["hello"])
        assert result.exit_code == 0
        assert "Hello, Environment!" in result.stdout


def test_hi_command_default() -> None:
    """Test hi command with default argument."""
    result = runner.invoke(app, ["hi"])
    assert result.exit_code == 0
    assert "Hi, Friend!" in result.stdout


def test_hi_command_with_name() -> None:
    """Test hi command with custom name."""
    result = runner.invoke(app, ["hi", "Bob"])
    assert result.exit_code == 0
    assert "Hi, Bob!" in result.stdout


def test_hi_command_with_env_variables() -> None:
    with (
        set_environ("MONO_ONE_NAME", "Environment"),
        set_environ("MONO_ONE_LANGUAGE", "japanese"),
    ):
        result = runner.invoke(app, ["hi"])
        assert result.exit_code == 0
        assert "ヤッホー, Environment!" in result.stdout


def test_hi_command_in_japanese() -> None:
    with set_environ("MONO_ONE_LANGUAGE", "japanese"):
        result = runner.invoke(app, ["hi", "匠"])
        assert result.exit_code == 0
        assert "ヤッホー, 匠!" in result.stdout


def test_hi_from_config_file() -> None:
    result = runner.invoke(app, ["--env=test", "hi"])
    assert result.exit_code == 0
    assert "ヤッホー, Alice.ini!" in result.stdout


def test_bye_command_default() -> None:
    """Test bye command with default argument."""
    result = runner.invoke(app, ["bye"])
    assert result.exit_code == 0
    assert "Goodbye, Friend!" in result.stdout


def test_bye_command_with_name() -> None:
    """Test bye command with custom name."""
    result = runner.invoke(app, ["bye", "Charlie"])
    assert result.exit_code == 0
    assert "Goodbye, Charlie!" in result.stdout


def test_app_help() -> None:
    """Test that help message works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "A minimal Python CLI monorepo template" in result.stdout


def test_all_commands_in_help() -> None:
    """Test that all commands are listed in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "hello" in result.stdout
    assert "hi" in result.stdout
    assert "bye" in result.stdout


@contextmanager
def set_environ(key: str, value: str):
    try:
        environ[key] = value
        yield
    finally:
        del environ[key]
