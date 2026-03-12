# ruff: noqa: PT009,N805, TID252


from collections.abc import Iterator
from contextlib import contextmanager
from os import environ
from unittest import TestCase

from ..greetings import say_hi


class GreetingsTests(TestCase):
    def test_say_hi_defaults(t) -> None:
        ret = say_hi()
        t.assertEqual(ret, "Hi, Friend!")

    def test_say_hi(t) -> None:
        name = "+tester+"
        language = "english"
        ret = say_hi(name=name, language=language)

        t.assertEqual(ret, f"Hi, {name}!")

    def test_say_hi_configurable_via_environment(t) -> None:
        name = "+env-name+"
        with (
            set_environ("MONO_ONE_NAME", name),
            set_environ("MONO_ONE_LANGUAGE", "japanese"),
        ):
            ret = say_hi()
            t.assertEqual(f"ヤッホー, {name}!", ret)


@contextmanager
def set_environ(key: str, value: str) -> Iterator[None]:
    try:
        environ[key] = value
        yield
    finally:
        del environ[key]
