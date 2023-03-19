import pytest
from ploomber_core.io import pretty_print


@pytest.mark.parametrize(
    "value, delimiter, last_delimiter, expected_result",
    [
        [["a_one", "b_two", "c_three"], ",", "or", "'a_one', 'b_two', or 'c_three'"],
        [["a_one", "b_two", "c_three"], ",", "and", "'a_one', 'b_two', and 'c_three'"],
        [["a_one", "b_two", "c_three"], "@", "and", "'a_one'@ 'b_two'@ and 'c_three'"],
        [["one"], ",", "and", "'one'"],
        [["one", "two"], ",", "and", "'one', and 'two'"],
        [[None, "two"], ",", "and", "'None', and 'two'"],
        [[None], ",", "and", "'None'"],
        [[1, 2, 3], ",", "or", "'1', '2', or '3'"],
    ],
)
def test_iterable(value, delimiter, last_delimiter, expected_result):
    assert (
        pretty_print.iterable(value, delimiter=delimiter, last_delimiter=last_delimiter)
        == expected_result
    )
