"""Greeting functionality for package one."""

from __future__ import annotations

from .conf import configurable


@configurable
def say_hi(cfg, name: str = "", language: str = "") -> str:
    """Say hi to someone."""
    name = name or cfg.name
    language = language or cfg.language

    return f"{hi_lang_map[language]}, {name}!"


hi_lang_map = {
    "english": "Hi",
    "japanese": "ヤッホー",
}
