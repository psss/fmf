# coding: utf-8

from __future__ import unicode_literals, absolute_import
import unittest
import os
import tempfile
from fmf.base import Tree
from fmf.constants import PLUGIN_ENV
from fmf.plugin_loader import enabled_plugins
from shutil import rmtree, copytree

PATH = os.path.dirname(os.path.realpath(__file__))
EXAMPLES = os.path.join(PATH, "..", "tests_plugin")
PLUGIN_PATH = os.path.join(PATH, "..", "..", "fmf", "plugins")


class Base(unittest.TestCase):
    def setUp(self):
        self.test_path = EXAMPLES
        self.tempdir = tempfile.mktemp()
        copytree(self.test_path, self.tempdir)
        # ensure the cache is cleared, to ensure that plugis are not already stored
        enabled_plugins.cache_clear()

    def tearDown(self):
        enabled_plugins.cache_clear()
        rmtree(self.tempdir)


class Pytest(Base):
    """ Verify reading data done via plugins """

    def setUp(self):
        super().setUp()
        os.environ[PLUGIN_ENV] = os.path.abspath(
            os.path.join(PLUGIN_PATH, "pytest.py"))
        self.plugin_tree = Tree(self.tempdir)

    def test_basic(self):
        item = self.plugin_tree.find("/test_basic/test_skip")
        self.assertFalse(item.data["enabled"])
        self.assertIn("Jan", item.data["author"])
        self.assertIn(
            "python3 -m pytest -m '' -v test_basic.py::test_skip", item.data
            ["test"])

    def test_modify(self):
        item = self.plugin_tree.find("/test_basic/test_pass")
        self.assertNotIn("duration", item.data)
        self.assertIn("Tier1", item.data["tag"])
        self.assertNotIn("tier2", item.data["tag"])
        self.assertEqual("0", item.data["tier"])
        with item as data:
            data["tag"].append("tier2")
            data["duration"] = ("10m")
            data.pop("tier")
        self.plugin_tree = Tree(self.tempdir)
        item = self.plugin_tree.find("/test_basic/test_pass")
        self.assertIn("duration", item.data)
        self.assertEqual("10m", item.data["duration"])
        self.assertIn("Tier1", item.data["tag"])
        self.assertIn("tier2", item.data["tag"])
        self.assertIn("tier2", item.data["tag"])
        self.assertNotIn("tier", item.data)


class Bash(Base):
    """ Verify reading data done via plugins """

    def setUp(self):
        super().setUp()
        os.environ[PLUGIN_ENV] = os.path.abspath(
            os.path.join(PLUGIN_PATH, "bash.py"))
        self.plugin_tree = Tree(self.tempdir)

    def test_pytest_plugin(self):
        item = self.plugin_tree.find("/runtest")
        self.assertIn("tier1", item.data["tag"])
        self.assertIn("./runtest.sh", item.data["test"])
        self.assertIn("Jan", item.data["author"])
