# ruff: noqa: PT009,N805, TID252

from unittest import TestCase

from ..database import KEY2_DEFAULT, DatabaseClient


class DatabaseClientTests(TestCase):
    def setUp(t):
        t.k1 = "+k1+"
        t.k2 = "+k2+"

    def test_Config(t):  # noqa: N802
        with t.subTest("defaults"):
            conf = DatabaseClient.Config(key1="+required+")
            t.assertEqual(conf.key1, "+required+")
            t.assertEqual(conf.key2, KEY2_DEFAULT)

        with t.subTest("parameters"):
            conf = DatabaseClient.Config(key1=t.k1, key2=t.k2)
            t.assertEqual(conf.key1, t.k1)
            t.assertEqual(conf.key2, t.k2)

    def test___init__(t):
        dc = DatabaseClient(key1=t.k1, key2=t.k2)
        t.assertEqual(dc.key1, t.k1)
        t.assertEqual(dc.key2, t.k2)

    def test_from_config(t):
        config = DatabaseClient.Config(key1=t.k1, key2=t.k2)
        dc = DatabaseClient.from_config(config=config)
        t.assertEqual(dc.key1, t.k1)
        t.assertEqual(dc.key2, t.k2)

    def test_fetch_data(t):
        dc = DatabaseClient(key1=t.k1, key2=t.k2)
        t.assertEqual(
            dc.fetch_data(),
            f"DatabaseClient data: key1={t.k1}, key2={t.k2}",
        )
