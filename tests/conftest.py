from mimic import StasisTrap
import pytest


@pytest.fixture
def trap():
    return StasisTrap()
