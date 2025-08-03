import pytest

from jiggle_version.parse_version.parse_dunder_version import find_by_ast


@pytest.mark.parametrize(
    "input_line, expected_output",
    [
        # Standard cases
        ('__version__ = "1.2.3"', "1.2.3"),
        ("__version__ = '0.5.alpha'", "0.5.alpha"),
        ("__version__ = (1, 2, 3)", "1.2.3"),
        ("__version__ = [0, 5, 'beta']", "0.5.beta"),
        ("__version__ = 1", "1"),
        ("__version__ = 1.0", "1.0"),

        # Edge cases
        ('__version__="1.2.3"', "1.2.3"), # No spaces
        ('   __version__ = "1.2.3"', "1.2.3"), # Leading whitespace
        ("", ""), # Empty string input

        # Cases that should not match
        ("version = '1.0'", None), # Wrong token
        ("# __version__ = '1.0'", None), # Commented out
        ("__version__ = get_version()", None), # Function call
        ("invalid syntax", None), # Invalid Python code
    ],
)
def test_find_by_ast(input_line, expected_output):
    """
    Tests the find_by_ast function with various inputs.
    """
    assert find_by_ast(input_line) == expected_output

@pytest.mark.parametrize(
    "input_line, token, expected_output",
    [
        ('__api_version__ = "1.0"', "__api_version__", "1.0"),
        ('VERSION = (1, 0)', "VERSION", "1.0"),
    ]
)
def test_find_by_ast_with_custom_token(input_line, token, expected_output):
    """
    Tests the function with a custom version token.
    """
    assert find_by_ast(input_line, version_token=token) == expected_output