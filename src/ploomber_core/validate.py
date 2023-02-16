import difflib
from ploomber_core.exceptions import ValidationError
from ploomber_core.io import pretty_print
import collections.abc


def _is_set_or_sequence(obj) -> bool:
    """
    Checks if obj is a sequence or a set.
    Returns False if obj is a string.
    """
    if isinstance(obj, str):
        return False

    return isinstance(obj, (collections.abc.Sequence, set))


def keys(valid, passed, name='spec', show_matches=True):
    """
    Checks if given values are valid. If not, raises an error with
    suggested valid values.

    Parameters
    ----------
    valid : list
        A list of valid values

    passed : str, list, tuple, or a set
        The value to check

    required : list
        Required values

    name : str, default 'spec'
        The name of the parameter

    show_matches : bool, default True
        Show suggested values in the error message

    Raises
    ------
    ValidationError if passed elements are not in valid
    """
    is_set_or_sequence = _is_set_or_sequence(passed)

    if not is_set_or_sequence or passed is None:
        passed = [passed]

    passed = set(passed)

    if valid:
        extra = passed - set(valid)

        if extra:

            err_message = f"Error validating argument '{name}', "

            if len(extra) < 2:
                err_message += "the following value isn't valid: "
            else:
                err_message += "the following values aren't valid: "

            err_message += f"{pretty_print.iterable(extra)}. "

            if len(valid) > 0:
                err_message += f"Valid values are: {pretty_print.iterable(valid)}. "

            if show_matches:
                input = str(passed.pop()) if len(passed) == 1 else passed
                input_matches = get_formatted_close_matches(input, valid)
                if len(input_matches) > 0:
                    err_message += f"\nDid you mean {input_matches}?"

            raise ValidationError(err_message)


def get_formatted_close_matches(input, valid) -> str:
    """
    Returns a formatted string of the best "good enough" matches
    """
    close_matches = []

    valid = list(str(i) for i in valid)

    if len(valid) > 0 and len(input) > 0:
        if _is_set_or_sequence(input):
            for i in input:
                if not isinstance(i, str):
                    i = str(i)
                input_matches = difflib.get_close_matches(i, valid)
                close_matches += input_matches
        else:
            close_matches = difflib.get_close_matches(str(input), valid)

        # remove dups
        close_matches = list(set(close_matches))
        close_matches = pretty_print.iterable(close_matches, last_delimiter="or")

    return close_matches
