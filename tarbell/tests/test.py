import os
import unittest
from tarbell.app import TarbellSite


class TarbellTestCase(unittest.TestCase):
    def setUp(self):
        """ Get a fake Tarbell site instance. """
        test_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'example')

        self.site = TarbellSite(test_dir)
        self.test_context = self.site.get_context()

    def test_worksheet_name_slugify(self):
        assert self.test_context.get('worksheet_with_spaces')
        assert not self.test_context.get('worksheet with spaces')


if __name__ == '__main__':
    unittest.main()
