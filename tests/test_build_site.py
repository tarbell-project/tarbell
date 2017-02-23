# -*- coding: utf-8 -*-
"""
Suite of tests that ensure an example project is built to spec.
Given a project with a pre-built _site directory, each test should
build the site and make sure it matches the pre-built version.
"""

import filecmp
import os
import py.path

from tarbell.app import EXCLUDES, TarbellSite

class SiteTest(object):
    """
    A Tarbell site to test. It should have a pre-built _site directory.
    """
    def __init__(self, path, name):
        self.path = py.path(path)
        self.name = name
        self.site = TarbellSite(str(self.path))

    def test_get_site(self):
        assert os.path.realpath(self.site.path) == os.path.realpath(self.path)
        assert self.site.project.name == self.name

    def test_default_excludes(self):
        "Ensure a basic set of excluded files"
        assert set(self.site.project.EXCLUDES) == set(EXCLUDES)


    def test_generate_site(self, tmpdir):
        "Generate a static site matching what's in _site"
        self.site.generate_static_site(str(tmpdir))

        # compare directories
        built = os.path.join(self.path, '_site')
        comp = filecmp.dircmp(built, str(tmpdir))

        assert set(comp.same_files) == set(os.listdir(built))
