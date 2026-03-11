from unittest import TestCase

from ..greetings import say_hi
from ..conf import get_config


class GreetingsTests(TestCase):
    def test_say_hi(t):
        name = "+tester+"
        language = "english"
        ret = say_hi(name=name, language=language)

        t.assertEqual(ret, f"Hi, {name}")

    def test_say_hi_configurable(t):
        name = "+env-name+"
        environ["MONO_ONE_NAME"] = name
        environ["MONO_ONE_LANGUAGE"] = "japanese"
        cfg = get_config()

        ret = say_hi(cfg=cfg)

        t.assertEqual(ret, f"ヤッホー, {name}")
