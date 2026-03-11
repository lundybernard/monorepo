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


def test_hi_command_with_env_variable() -> None:
    with set_environ("MONO_ONE_NAME", "Environment"):
        result = runner.invoke(app, ["hi"])
        assert result.exit_code == 0
        assert "Hi, Environment!" in result.stdout


def test_hi_command_in_japanese() -> None:
    with set_environ("MONO_ONE_LANGUAGE", "japanese"):
        result = runner.invoke(app, ["hi", "匠"])
        assert result.exit_code == 0
        assert "ヤッホー, 匠!" in result.stdout


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
