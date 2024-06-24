"""
Unit and regression test for the CoolerChips package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import CoolerChips


def test_CoolerChips_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "CoolerChips" in sys.modules
