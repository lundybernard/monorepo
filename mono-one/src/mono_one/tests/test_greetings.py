# ruff: noqa: PT009,N805, TID252

from unittest import TestCase

from ..greetings import hi_lang_map, say_hi


class GreetingsTests(TestCase):
    def test_say_hi_defaults(t) -> None:
        ret = say_hi()
        t.assertEqual(ret, "Hi, Friend!")

    def test_say_hi(t) -> None:
        name = "+tester+"
        language = "english"
        ret = say_hi(name=name, language=language)

        t.assertEqual(ret, f"Hi, {name}!")

    def test_say_hi_languags(t) -> None:
        name = "+tester+"
        for language, greeting in hi_lang_map.items():
            with t.subTest(language):
                ret = say_hi(name=name, language=language)
                t.assertEqual(f"{greeting}, {name}!", ret)
