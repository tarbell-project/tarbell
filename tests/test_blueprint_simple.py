# -*- coding: utf-8 -*-
"""
Tests for the barebones example project
"""
import filecmp
import os

from tarbell.app import EXCLUDES, TarbellSite

TESTS_DIR = os.path.dirname(__file__)
PATH = os.path.realpath(os.path.join(TESTS_DIR, 'examples/blueprint-simple'))
BUILT = os.path.join(PATH, '_site')

PROJECT_NAME = "blueprint-test"

def test_get_site():
    site = TarbellSite(PATH)

    assert os.path.realpath(site.path) == os.path.realpath(PATH)
    assert site.project.name == PROJECT_NAME


def test_default_excludes():
    "Ensure a basic set of excluded files"
    site = TarbellSite(PATH)

    assert set(site.project.EXCLUDES) == set(EXCLUDES)


def test_blueprint_path():
	"Make sure blueprint is loading correctly"
	site = TarbellSite(PATH)

	assert os.path.realpath(site.base.base_dir) == os.path.realpath(os.path.join(PATH, '_blueprint'))
