import os
import unittest
from tarbell.app import TarbellSite


class TarbellTestCase(unittest.TestCase):
    def setUp(self):
        """ Get a fake Tarbell site instance. """
        test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'example')
        self.site = TarbellSite(test_dir)
        default_spreadsheet = self.site.projects['project'].GOOGLE_DOC
        self.test_context = self.site.get_context_from_gdoc(**default_spreadsheet)
        import pprint
        pprint.pprint(self.test_context)
        import ipdb; ipdb.set_trace();

    def test_worksheet_name_slugify(self):
        assert self.test_context.get('worksheet_with_spaces')
        assert not self.test_context.get('worksheet with spaces')

    def test_string_value(self):
        assert isinstance(self.test_context['string_value'], str)

    def test_integer_value(self):
        assert isinstance(self.test_context['integer_value'], (int, long))

    def test_float_value(self):
        assert isinstance(self.test_context['float_value'], float)


if __name__ == '__main__':
    unittest.main()
