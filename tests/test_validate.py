import pytest
from ploomber_core import validate
from ploomber_core.exceptions import MissingKeysValidationError, ValidationError


@pytest.mark.parametrize(
    "input, valid_keys, key_name, sorted_valid_keys," +
    "expected_suggestions, expected_invalid_keys_message",
    [
        [
            "a_oen", ["a_one", "b_two", "c_three", "d_four"], "input",
            "'a_one', 'b_two', 'c_three', and 'd_four'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],
        [
            None, ["a_one", "b_two", "c_three", "d_four"], "input",
            "'a_one', 'b_two', 'c_three', and 'd_four'", "'a_one'",
            "the following value isn't valid: 'None'"
        ],
        [
            ["a_oen"], ["a_one", "b_two", "c_three", "d_four"], "input",
            "'a_one', 'b_two', 'c_three', and 'd_four'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],

        [
            ["a_oen"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],
        [
            ["a_oen", "b_two"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],
        [
            ["a_oen", "b_tow"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following values aren't valid: 'a_oen', and 'b_tow'"
        ],
        [
            ["a_oen"], ["a_one"], "input",
            "'a_one'", "'a_one'", "the following value isn't valid: 'a_oen'"
        ],
        [
            [None], ["a_one"], "input",
            "'a_one'", "'a_one'", "the following value isn't valid: 'None'"
        ],
        [
            [None], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'", "the following value isn't valid: 'None'"
        ],
        [
            [None, "b_two"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'", "the following value isn't valid: 'None'"
        ],
        [
            [None, "b_tow"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following values aren't valid: 'None', and 'b_tow'"
        ],
        [
            ["b_tow"], [None, "b_two"], "input",
            "'None', and 'b_two'", "'b_two'", "the following value isn't valid: 'b_tow'"
        ],
        [
            1, [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10'",
            "the following value isn't valid: '1'"
        ],
        [
            [1], [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10'",
            "the following value isn't valid: '1'"
        ],
        [
            [1, 2], [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10', or '20'",
            "the following values aren't valid: '1', and '2'"
        ],
        [
            (1, 2), [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10', or '20'",
            "the following values aren't valid: '1', and '2'"
        ],
        [
            {1, 2, 3}, [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10', '20', or '30'",
            "the following values aren't valid: '1', '2', and '3'"
        ],
    ],
)
def test_invalid_input_keys_with_suggestions(input, valid_keys, key_name,
                                             sorted_valid_keys, expected_suggestions,
                                             expected_invalid_keys_message):

    with pytest.raises(ValidationError) as err:
        validate.keys(valid=valid_keys,
                      passed=input,
                      name=key_name)

    assert f"""Error validating argument '{key_name}',""" in str(err.value)
    assert expected_invalid_keys_message in str(err.value)
    assert f"""Valid values are: {sorted_valid_keys}.""" in str(
        err.value)
    assert f"""Did you mean {expected_suggestions}""" in str(err.value)


@pytest.mark.parametrize(
    "input, valid_keys, key_name, sorted_valid_keys, expected_invalid_keys_message",
    [
        [
            ["qwe"], ["a_one", "b_two", "c_three", "d_four"], "input",
            "'a_one', 'b_two', 'c_three', and 'd_four'",
            "the following value isn't valid: 'qwe'"
        ],

        [
            ["qwe"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "the following value isn't valid: 'qwe'"
        ],
        [
            ["qwe"], ["a_one"], "input",
            "'a_one'", "the following value isn't valid: 'qwe'"
        ],
        [
            [""], ["a_one"], "input",
            "'a_one'", "the following value isn't valid: ''"
        ],
        [
            [None], ["b_two"], "input",
            "'b_two'", "the following value isn't valid: 'None'"
        ],
        [
            ["qwe", "abc"], ["a_one"], "input",
            "'a_one'", "the following values aren't valid: 'abc', and 'qwe'"
        ],
        [
            "qwe", ["a_one"], "input",
            "'a_one'", "the following value isn't valid: 'qwe'"
        ],
    ],
)
def test_invalid_input_keys_without_suggestions(input, valid_keys, key_name,
                                                sorted_valid_keys,
                                                expected_invalid_keys_message):

    with pytest.raises(ValidationError) as err:
        validate.keys(valid=valid_keys,
                      passed=input,
                      name=key_name)

    assert f"""Error validating argument '{key_name}',""" in str(err.value)
    assert expected_invalid_keys_message in str(err.value)
    assert f"""Valid values are: {sorted_valid_keys}.""" in str(err.value)
    assert """Did you mean""" not in str(err.value)


@pytest.mark.parametrize(
    "input, valid_keys, key_name, sorted_valid_keys," +
    "expected_suggestions, expected_message",
    [
        [
            "a_oen", ["a_one", "b_two", "c_three", "d_four"], "input",
            "'a_one', 'b_two', 'c_three', and 'd_four'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],
        [
            None, ["a_one", "b_two", "c_three", "d_four"], "input",
            "'a_one', 'b_two', 'c_three', and 'd_four'", "'a_one'",
            "the following value isn't valid: 'None'"
        ],
        [
            ["a_oen"], ["a_one", "b_two", "c_three", "d_four"], "input",
            "'a_one', 'b_two', 'c_three', and 'd_four'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],

        [
            ["a_oen"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],
        [
            ["a_oen", "b_two"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following value isn't valid: 'a_oen'"
        ],
        [
            ["a_oen", "b_tow"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following values aren't valid: 'a_oen', and 'b_tow'"
        ],
        [
            ["a_oen"], ["a_one"], "input",
            "'a_one'", "'a_one'", "the following value isn't valid: 'a_oen'"
        ],
        [
            [None], ["a_one"], "input",
            "'a_one'", "'a_one'", "the following value isn't valid: 'None'"
        ],
        [
            [None], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'", "the following value isn't valid: 'None'"
        ],
        [
            [None, "b_two"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'", "the following value isn't valid: 'None'"
        ],
        [
            [None, "b_tow"], ["a_one", "b_two"], "input",
            "'a_one', and 'b_two'", "'a_one'",
            "the following values aren't valid: 'None', and 'b_tow'"
        ],
        [
            ["b_tow"], [None, "b_two"], "input",
            "'None', and 'b_two'", "'b_two'", "the following value isn't valid: 'b_tow'"
        ],
        [
            1, [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10'",
            "the following value isn't valid: '1'"
        ],
        [
            [1], [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10'",
            "the following value isn't valid: '1'"
        ],
        [
            [1, 2], [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10', or '20'",
            "the following values aren't valid: '1', and '2'"
        ],
        [
            (1, 2), [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10', or '20'",
            "the following values aren't valid: '1', and '2'"
        ],
        [
            {1, 2, 3}, [10, 20, 30, 40], "input",
            "'10', '20', '30', and '40'", "'10', '20', or '30'",
            "the following values aren't valid: '1', '2', and '3'"
        ],
    ],
)
def test_invalid_input_keys_with_suggestions_show_matches_false(input, valid_keys,
                                                                key_name,
                                                                sorted_valid_keys,
                                                                expected_suggestions,
                                                                expected_message):

    with pytest.raises(ValidationError) as err:
        validate.keys(valid=valid_keys,
                      passed=input,
                      show_matches=False,
                      name=key_name)

    assert f"""Error validating argument '{key_name}',""" in str(err.value)
    assert expected_message in str(err.value)
    assert f"""Valid values are: {sorted_valid_keys}.""" in str(
        err.value)
    assert f"""Did you mean {expected_suggestions}""" not in str(err.value)


@pytest.mark.parametrize(
    "passed, valid_keys, key_name, required, missing_keys",
    [
        [
            "input_a", [], "input_a", ["input_a", "input_b", "input_c"],
            "'input_b', and 'input_c'"
        ],

        [
            "input_a", ["input_a"], "input_a",
            ["input_a", "input_b", "input_c"], "'input_b', and 'input_c'"
        ],
        [
            "input_a", ["input_a", "input_b"], "input_a", [
                "input_a", "input_b"], "'input_b'"
        ],
    ],
)
def test_missing_input_keys(passed, valid_keys, key_name, required, missing_keys):

    with pytest.raises(MissingKeysValidationError) as err:
        validate.keys(valid=valid_keys,
                      passed=[passed],
                      required=required,
                      name=key_name)

    assert f"""Error validating argument {key_name}.""" in str(err.value)
    assert f"""Missing keys: {missing_keys}""" in str(err.value)


@pytest.mark.parametrize(
    "passed, valid_keys, key_name",
    [
        [
            [10], [10, 20, 30, 40], "input"
        ],
        [
            10, [10, 20, 30, 40], "input"
        ],
        [
            ["a_one"], ["a_one", "b_two", "c_three", "d_four"], "input"
        ],
        [
            ["a_one", "b_two"], ["a_one", "b_two", "c_three", "d_four"], "input"
        ],
        [
            ("a_one", "b_two"), ["a_one", "b_two", "c_three", "d_four"], "input"
        ],
        [
            {"a_one", "b_two"}, ["a_one", "b_two", "c_three", "d_four"], "input"
        ],
        [
            ["a_one"], ["a_one", "b_two"], "input"
        ],
        [
            "a_one", ["a_one"], "input"
        ],
        [
            None, ["a_one", None], "input"
        ],
        [
            [None], ["a_one", None], "input"
        ],
    ],
)
def test_valid_input_keys(passed, valid_keys, key_name):
    validate.keys(valid=valid_keys,
                  passed=passed,
                  name=key_name)


@pytest.mark.parametrize(
    "passed, valid_keys, key_name, required",
    [
        [
            ["a_one"], ["a_one", "b_two", "c_three", "d_four"], "input", ["a_one"]
        ],
        [
            ["a_one"], ["a_one", "b_two"], "input", ["a_one"]
        ],
        [
            "a_one", ["a_one"], "input", ["a_one"]
        ],
        [
            None, ["a_one", None], "input", [None]
        ],
        [
            [None], ["a_one", None], "input", [None]
        ],
        [
            ["a_one", "b_two"], ["a_one", "b_two"], "input", ["a_one", "b_two"]
        ],
        [
            ["a_one", "b_two"], ["a_one", "b_two", "c_three",
                                 "d_four"], "input", ["a_one", "b_two"]
        ],
    ],
)
def test_required_valid_input_keys(passed, valid_keys, key_name, required):
    validate.keys(valid=valid_keys,
                  passed=passed,
                  required=required,
                  name=key_name)


@pytest.mark.parametrize(
    "value, valid, expected_matches",
    [
        [
            "one", ["one", "two", "three"], "'one'"
        ],
        [
            "abc", ["abcd", "abcde", "three"], "'abcd', or 'abcde'"
        ],
        [
            ["abc", "thr"], ["abcd", "abcde", "three"], "'abcd', 'abcde', or 'three'"
        ],
    ],
)
def test_get_formatted_close_matches(value, valid, expected_matches):
    match_result = validate.get_formatted_close_matches(value, valid)
    assert match_result == expected_matches
