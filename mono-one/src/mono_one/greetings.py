"""Greeting functionality for package one."""

from __future__ import annotations


def say_hi(name: str = "Friend", language: str = "english") -> str:
    """Generate a greeting in the specified language."""
    return f"{hi_lang_map[language]}, {name}!"


hi_lang_map = {
    "english": "Hi",
    "japanese": "ヤッホー",
}
