"""Docstring."""
import unittest

from myrandom import Random

# import dense_ev
from dense_ev._test_ops import unit_test


class TestRandom(unittest.TestCase):
    """Tests Random class implementation."""

    def test_run(self):
        """Tests run method random."""
        random = Random()

        self.assertEqual(random.run(2), 4)


class TestRmatrix(unittest.TestCase):
    """Test rmatrix function."""

    def test_run(self):
        unit_test(2)
        self.assertEqual(1, 1)
