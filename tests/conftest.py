from mimics import StasisTrap
import pytest


@pytest.fixture
def trap():
    return StasisTrap()
