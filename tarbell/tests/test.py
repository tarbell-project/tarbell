import os
import unittest
from tarbell.app import TarbellSite


class TarbellSiteTestCase(unittest.TestCase):
    """
    Tests for the TarbellSite class methods.
    """
    def setUp(self):
        """ Get a fake Tarbell site instance. """
        test_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'example')

        self.site = TarbellSite(test_dir)

    def test_init(self):
        self.assertRaises(TypeError, TarbellSite, )

    @unittest.skip('')
    def test_filter_files(self, path):
        pass

    @unittest.skip('')
    def test_sort_modules(self, x, y):
        pass

    @unittest.skip('')
    def test_load_projects(self):
        pass

    @unittest.skip('')
    def test_preview(self, path=None):
        pass

    @unittest.skip('')
    def test_get_context(self):
        pass

    @unittest.skip('')
    def test_get_context_from_csv(self):
        pass

    @unittest.skip('')
    def test_get_context_from_gdoc(self):
        pass

    @unittest.skip('')
    def test__get_context_from_gdoc(self, key, **kwargs):
        pass

    @unittest.skip('')
    def test_export_xlsx(self, key):
        pass

    @unittest.skip('')
    def test_process_xlsx(self, content):
        pass

    @unittest.skip('')
    def test_copy_global_values(self, data):
        pass

    @unittest.skip('')
    def test_make_headers(self, worksheet):
        pass

    @unittest.skip('')
    def test_make_worksheet_data(self, headers, worksheet):
        pass

    @unittest.skip('')
    def test_generate_static_site(self, output_root):
        pass


if __name__ == '__main__':
    unittest.main()
