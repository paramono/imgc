import unittest
from unittest.mock import patch

from imgc.image import ImageSize


class ImageSizeTest(unittest.TestCase):

    def test_parse_raises_on_wrong_type(self):
        size = {}
        with self.assertRaises(TypeError):
            ImageSize.parse(size)

    @patch('imgc.image.ImageSize._parse_tuple')
    def test_parse_processes_iterables(self, parse_tuple):
        size = (800, 600,)
        ImageSize.parse(size)
        self.assertEqual(parse_tuple.call_count, 1)
        parse_tuple.assert_called_with(size, None)

        size = [800, 600]
        ImageSize.parse(size)
        self.assertEqual(parse_tuple.call_count, 2)
        parse_tuple.assert_called_with(size, None)

    @patch('imgc.image.ImageSize._parse_string')
    def test_parse_processes_strings(self, parse_string):
        size = '800x600'
        ImageSize.parse(size)
        self.assertEqual(parse_string.call_count, 1)
        parse_string.assert_called_with(size, None)
