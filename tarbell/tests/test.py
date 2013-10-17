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
        """
        Creating an instance of TarbellSite without a path
        raises a TypeError exception.
        """
        self.assertRaises(TypeError, TarbellSite, )

    def test_filter_files(self):
        name, project, project_path = self.site.projects[0]

        filtered = self.site.filter_files(project_path)
        next = filtered.next()

        """
        Each project tuple has a length of 3
        """
        self.assertEqual(len(next), 3)

        """
        The first item in the project tuple equals the project_path passed
        """
        self.assertEqual(project_path, next[0])

    def test_sort_modules(self):
        """
        Our "base" project is always the last item in the
        return list of sorted modules
        """
        projects = sorted(self.site.projects, cmp=self.site.sort_modules)
        self.assertEqual(projects[-1][0], "base")

    def test_load_projects(self):
        """
        Load projects returns a list with length of 2, since our test app
        has two sub directories: base and project.
        """
        self.assertEqual(len(self.site.load_projects()), 2)

    @unittest.skip('')
    def test_preview(self):
        pass

    def test_get_context(self):
        """
        Our get_context method should return a dictionary
        """
        self.assertTrue(isinstance(self.site.get_context(), dict))

    def test_get_context_from_csv(self):
        """
        Our get_context_from_csv should fetch a local file path or an url
        """
        self.assertTrue(isinstance(self.site.get_context_from_csv(), dict))

        self.site.CONTEXT_SOURCE_FILE = 'https://raw.github.com/newsapps/'
        'flask-tarbell/0.9/tarbell/tests/example/project/data/project.csv'

        self.assertTrue(isinstance(self.site.get_context_from_csv(), dict))

    @unittest.skip('')
    def test_get_context_from_gdoc(self):
        pass

    @unittest.skip('')
    def test__get_context_from_gdoc(self):
        pass

    @unittest.skip('')
    def test_export_xlsx(self):
        pass

    @unittest.skip('')
    def test_process_xlsx(self):
        pass

    @unittest.skip('')
    def test_copy_global_values(self):
        pass

    @unittest.skip('')
    def test_make_headers(self):
        pass

    @unittest.skip('')
    def test_make_worksheet_data(self):
        pass

    @unittest.skip('')
    def test_generate_static_site(self):
        pass


if __name__ == '__main__':
    unittest.main()
