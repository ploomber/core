import warnings
from functools import wraps

from ploomber_core.warnings import PloomberDeprecationWarning

COMMUNITY = "If you need help migrating, contact us: https://ploomber.io/community"


def parameter_renamed(
    deprecated_in,
    remove_in,
    *,
    old_name,
    old_value,
    new_name,
    new_value,
    custom_message=None,
):
    """

    Notes
    -----
    .. versionadded:: 0.1
    """

    using_old_parameter = old_value != "deprecated"

    if using_old_parameter:
        warnings.warn(
            f"{old_name!r} was renamed to {new_name!r} in version "
            f"{deprecated_in}. {old_name!r} will be removed in "
            f"{remove_in}. {_message_end(custom_message)}",
            PloomberDeprecationWarning,
        )

    return old_value if using_old_parameter else new_value


def parameter_deprecated(deprecated_in, remove_in, *, name_old, value_passed):
    """

    Notes
    -----
    .. versionadded:: 0.1
    """
    warn = value_passed != "deprecated"

    if warn:
        warnings.warn(
            f"{name_old!r} was deprecated in version "
            f"{deprecated_in}. {name_old!r} will be removed "
            f"in {remove_in}. {COMMUNITY}",
            PloomberDeprecationWarning,
        )

    return warn


def parameter_default_changed(
    changed_in,
    *,
    name,
    old_default,
    new_default,
    value,
):
    """

    Notes
    -----
    .. versionadded:: 0.1
    """
    using_default = value == "warn"

    if using_default:
        warnings.warn(
            f"The default value of {name} will change from {old_default!r} to "
            f"{new_default!r} in {changed_in}.",
            PloomberDeprecationWarning,
        )

    return old_default if using_default else value


def _message_end(custom_message):
    if custom_message:
        return f"{custom_message}. {COMMUNITY}"
    else:
        return COMMUNITY


def function(deprecated_in, remove_in, *, new_name=None, custom_message=None):
    """A decorator for deprecated functions

    Notes
    -----
    .. versionadded:: 0.1
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            what = "deprecated" if not new_name else f"renamed to {new_name!r}"
            name_old = fn.__name__
            warnings.warn(
                f"Function {name_old!r} was "
                f"{what} in version {deprecated_in}. {name_old!r} will be "
                f"removed in version {remove_in}. {_message_end(custom_message)}",
                category=PloomberDeprecationWarning,
            )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def method(deprecated_in, remove_in, *, new_name=None, custom_message=None):
    """A decorator for deprecated methods

    Notes
    -----
    .. versionchanged:: 0.1
        Added ``new_name`` and ``custom_message``
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            what = "deprecated" if not new_name else f"renamed to {new_name!r}"
            name_old = fn.__name__
            warnings.warn(
                f"{name_old!r} from {type(self).__name__!r} was "
                f"{what} in version {deprecated_in}. {name_old!r} will be "
                f"removed in version {remove_in}. {_message_end(custom_message)}",
                category=PloomberDeprecationWarning,
            )
            return fn(self, *args, **kwargs)

        return wrapper

    return decorator
