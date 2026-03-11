"""Greeting functionality for package one."""

from __future__ import annotations

from .conf import configurable


@configurable
def say_hi(cfg, name: str = "", language: str = "") -> str:
    """Say hi to someone."""
    name = name if name else cfg.name
    language = language if language else cfg.language

    return f"{hi_lang_map[language]}, {name}!"


hi_lang_map = {
    "english": "Hi",
    "japanese": "ヤッホー",
}
