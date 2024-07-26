"""
Unit and regression test for the mostcool package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import mostcool


def test_mostcool_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "mostcool" in sys.modules
