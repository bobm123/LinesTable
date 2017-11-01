"""
You can auto-discover and run all tests with this command:

    py.test

Documentation: https://docs.pytest.org/en/latest/
"""

from offset2solid import fie_to_di


def test_fie_conversion():
    # change these to asserts, put in tests
    assert fie_to_di("0-0-0") == 0.0
    assert fie_to_di("1-0-0") == 12.0
    assert fie_to_di("0-1-0") == 1.0
    assert fie_to_di("0-0-1") == .125
    assert fie_to_di("4-4-4") == 52.5
