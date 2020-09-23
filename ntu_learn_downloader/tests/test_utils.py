import unittest

from ntu_learn_downloader.tests.mock_server import MOCK_CONSTANTS
from ntu_learn_downloader.utils import get_video_download_size, get_filename_from_url, sanitise_filename


class TestUtils(unittest.TestCase):
    def test_get_video_download_size(self):
        expected = "7.28 MB"
        url = "http://localhost:8082/content/904d737e7d5f85318d127786285821d2/studio0578720023632e706a28abb9e8/media/1.mp4"
        result = get_video_download_size(url)
        self.assertEqual(expected, result)

    def test_get_filename_from_url(self):
        path = "/bbcswebdav/pid-1619585-dt-content-rid-6387676_1/courses/18S2-CE1007-CZ1007-C-LEC/LinearStructures%281%29.zip"
        expected = "LinearStructures(1).zip"
        filename = get_filename_from_url(path)
        self.assertEqual(expected, filename)

    def test_sanitise_filename(self):
        name = 'Week 1: Tutorial (1/2).mp4'
        self.assertEqual('Week 1 Tutorial (1-2).mp4', sanitise_filename(name))