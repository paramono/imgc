from argparse import ArgumentTypeError
import unittest

from imgc.utils.types import quality_type, size_type


class QualityTypeTest(unittest.TestCase):

    # integer tests #
    def test_int_value_too_low(self):
        value = 0
        with self.assertRaises(ArgumentTypeError):
            quality_type(value)

    def test_int_value_lowest(self):
        value = 1
        result = quality_type(value)
        self.assertEqual(result, 1)

    def test_int_value_middle(self):
        value = 90
        result = quality_type(value)
        self.assertEqual(result, 90)

    def test_int_value_highest(self):
        value = 100
        result = quality_type(value)
        self.assertEqual(result, 100)

    def test_int_value_too_high(self):
        value = 150
        with self.assertRaises(ArgumentTypeError):
            quality_type(value)

    # string tests #
    def test_str_value_too_low(self):
        value = '0'
        with self.assertRaises(ArgumentTypeError):
            quality_type(value)

    def test_str_value_lowest(self):
        value = '1'
        result = quality_type(value)
        self.assertEqual(result, 1)

    def test_str_value_middle(self):
        value = '90'
        result = quality_type(value)
        self.assertEqual(result, 90)

    def test_str_value_highest(self):
        value = '100'
        result = quality_type(value)
        self.assertEqual(result, 100)

    def test_value_too_high(self):
        value = '150'
        with self.assertRaises(ArgumentTypeError):
            quality_type(value)

    # wrong input #
    def test_wrong_input(self):
        value = 'whatever'
        with self.assertRaises(ArgumentTypeError):
            quality_type(value)


class SizeTypeTest(unittest.TestCase):
    pass
