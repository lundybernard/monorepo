"""Greeting functionality for package one."""

from __future__ import annotations

from .conf import configurable

# def say_hi(name: str = "Friend", language: str = "english") -> str:
#    """Say hi to someone."""
#    return f"{hi_lang_map[language]}, {name}!"


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
