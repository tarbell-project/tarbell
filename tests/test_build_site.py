# -*- coding: utf-8 -*-
"""
Suite of tests that ensure an example project is built to spec.
Given a project with a pre-built _site directory, each test should
build the site and make sure it matches the pre-built version.
"""
import filecmp
import os

import pytest

from tarbell.app import TarbellSite


EXAMPLES_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), 'examples'))
TEST_SITES = [os.path.join(EXAMPLES_DIR, d) for d in os.listdir(EXAMPLES_DIR)]


@pytest.mark.parametrize('path', TEST_SITES)
def test_site(path, tmpdir):
    """
    Test that sites in the examples/ directory build correctly
    """
    site = TarbellSite(path)

    assert os.path.realpath(site.path) == os.path.realpath(path)

    # build the site
    site.generate_static_site(str(tmpdir))

    # compare directories
    built = os.path.join(path, '_site')
    comp = filecmp.dircmp(built, str(tmpdir))

    assert set(comp.same_files) == set(os.listdir(built))

