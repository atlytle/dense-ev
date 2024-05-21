"""Docstring."""
import unittest
import sys

# from myrandom import Random
# from dense_ev._test_ops import unit_test, run_unit_tests, run_rtests
from dense_ev.decompose_pauli import test as dtest
# from dense_ev.rmatrix import check_random_H


'''
class TestRandom(unittest.TestCase):
    """Tests Random class implementation."""

    def test_run(self):
        """Tests run method random."""
        random = Random()

        self.assertEqual(random.run(2), 4)
'''


class TestDensePauli(unittest.TestCase):
    """Test DensePauliExpectation."""

    def test_run(self):
        # unit_test(2)
        # self.assertTrue(run_unit_tests(3, 4))
        # self.assertTrue(run_rtests())
        self.assertTrue(dtest())
        # self.assertTrue(check_random_H(3))
