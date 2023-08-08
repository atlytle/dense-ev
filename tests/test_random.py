"""Docstring."""
import unittest
import sys

# from myrandom import Random
from dense_ev._test_ops import unit_test, run_unit_tests


'''
class TestRandom(unittest.TestCase):
    """Tests Random class implementation."""

    def test_run(self):
        """Tests run method random."""
        random = Random()

        self.assertEqual(random.run(2), 4)
'''


class TestRmatrix(unittest.TestCase):
    """Test rmatrix function."""

    def test_run(self):
        # unit_test(2)
        self.assertTrue(run_unit_tests(3, 4))
