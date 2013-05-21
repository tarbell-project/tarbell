import os
import unittest
from tarbell.app import TarbellSite


class TarbellTestCase(unittest.TestCase):
    def setUp(self):
        """ Get a fake Tarbell site instance. """
        test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'example')
        self.site = TarbellSite(test_dir)
        self.test_context = self.site.get_context_from_gdoc(**self.site.projects['project'].GOOGLE_DOC)


    def tearDown(self):
        pass

    def test_string_value(self):
        assert isinstance(self.test_context['string_value'], str)

    def test_integer_value(self):
        assert isinstance(self.test_context['integer_value'], (int, long))

    def test_float_value(self):
        assert isinstance(self.test_context['float_value'], float)

    def test_spreadsheet_slugify(self):
        assert True


if __name__ == '__main__':
    unittest.main()
