"""Greeting functionality for package one."""

from __future__ import annotations

from typing import TypedDict, Unpack

from .conf import Configuration, configurable


class SayHiKwargs(TypedDict, total=False):
    name: str
    language: str


@configurable
def say_hi(*, cfg: Configuration, **kwargs: Unpack[SayHiKwargs]) -> str:
    """Say hi to someone."""
    name = kwargs.get("name") or cfg.name
    language = kwargs.get("language") or cfg.language

    return f"{hi_lang_map[language]}, {name}!"


hi_lang_map = {
    "english": "Hi",
    "japanese": "ヤッホー",
}
