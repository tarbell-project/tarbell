# -*- coding: utf-8 -*-
"""
Tests for the barebones example project
"""
import os
import py.path

from tarbell.app import EXCLUDES, TarbellSite

TESTS_DIR = os.path.dirname(__file__)
PATH = os.path.realpath(os.path.join(TESTS_DIR, 'examples/barebones'))


def test_get_site():
    site = TarbellSite(PATH)

    assert os.path.realpath(site.path) == os.path.realpath(PATH)
    assert site.project.name == "barebones"


def test_default_excludes():
    "Ensure a basic set of excluded files"
    site = TarbellSite(PATH)

    assert set(site.project.EXCLUDES) == set(EXCLUDES)


def test_generate_site(tmpdir):
    "Generate a static site matching what's in _site"
    site = TarbellSite(PATH)
    built = os.path.join(PATH, '_site')

    site.generate_static_site(str(tmpdir))

    files = set(f.basename for f in tmpdir.listdir())

    assert files == set(['data.json', 'index.html'])

