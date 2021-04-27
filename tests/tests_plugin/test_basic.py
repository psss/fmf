import pytest
import unittest
from fmf_metadata import FMF


@FMF.tag("Tier1")
@FMF.tier("0")
@FMF.summary("This is basic testcase")
def test_pass():
    assert True


def test_fail():
    assert False


@pytest.mark.skip
def test_skip():
    assert True


@pytest.mark.parametrize("test_input", ["a", "b", "c"])
def test_parametrize(test_input):
    assert bool(test_input)


class TestCls(unittest.TestCase):
    def test(self):
        self.assertTrue(True)
