import unittest
import util


class TimeFormatTest(unittest.TestCase):

    def test_is_time(self):
        self.assertFalse(util.is_time("AhBm"))
        self.assertFalse(util.is_time("hm"))
        self.assertFalse(util.is_time("4h"))
        self.assertFalse(util.is_time("10m"))
        self.assertFalse(util.is_time("4hm"))
        self.assertFalse(util.is_time("h4m"))
        self.assertFalse(util.is_time("A4h10m"))
        self.assertFalse(util.is_time("4h10mA"))
        self.assertFalse(util.is_time("4h1A0m"))
        self.assertFalse(util.is_time("4.0h10m"))

        self.assertTrue(util.is_time("4h10m"))
        self.assertTrue(util.is_time("222355h203402340m"))
        self.assertTrue(util.is_time("0h10m"))

    def test_to_readable_time(self):
        self.assertEqual(util.to_readable_time(60), "0h1m")
        self.assertEqual(util.to_readable_time(3600), "1h0m")
        self.assertEqual(util.to_readable_time(1000), "0h16m")
