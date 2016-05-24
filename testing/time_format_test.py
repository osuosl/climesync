import unittest
import climesync


class TimeFormatTest(unittest.TestCase):

    def test_is_time(self):
        self.assertFalse(climesync.is_time("AhBm"))
        self.assertFalse(climesync.is_time("hm"))
        self.assertFalse(climesync.is_time("4h"))
        self.assertFalse(climesync.is_time("10m"))
        self.assertFalse(climesync.is_time("4hm"))
        self.assertFalse(climesync.is_time("h4m"))
        self.assertFalse(climesync.is_time("A4h10m"))
        self.assertFalse(climesync.is_time("4h10mA"))
        self.assertFalse(climesync.is_time("4h1A0m"))
        self.assertFalse(climesync.is_time("4.0h10m"))

        self.assertTrue(climesync.is_time("4h10m"))
        self.assertTrue(climesync.is_time("222355h203402340m"))
        self.assertTrue(climesync.is_time("0h10m"))

    def test_to_readable_time(self):
        self.assertEqual(climesync.to_readable_time(60), "0h1m")
        self.assertEqual(climesync.to_readable_time(3600), "1h0m")
        self.assertEqual(climesync.to_readable_time(1000), "0h16m")
