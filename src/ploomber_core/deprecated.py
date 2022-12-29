import warnings
from functools import wraps

from ploomber_core.warnings import PloomberDeprecationWarning

COMMUNITY = "If you need help migrating, contact us: https://ploomber.io/community"


def parameter_renamed(
    deprecated_in, removed_in, name_old, name_new, value_passed, *, custom_message=None
):
    """

    Notes
    -----
    .. versionadded:: 0.1
    """

    warn = value_passed != "deprecated"

    if warn:
        warnings.warn(
            f"{name_old!r} was renamed to {name_new!r} in version "
            f"{deprecated_in}. {name_old!r} will be removed in "
            f"{removed_in}. {_message_end(custom_message)}",
            PloomberDeprecationWarning,
        )

    return warn


def parameter_deprecated(deprecated_in, removed_in, name_old, value_passed):
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
            f"in {removed_in}. {COMMUNITY}",
            PloomberDeprecationWarning,
        )

    return warn


def parameter_default_changed(removed_in, name, value_old, value_new, value_passed):
    """

    Notes
    -----
    .. versionadded:: 0.1
    """
    warn = value_passed == "warn"

    if warn:
        warnings.warn(
            f"The default value of {name} will change from {value_old!r} to "
            f"{value_new!r} in {removed_in}.",
            PloomberDeprecationWarning,
        )

    return warn


def _message_end(custom_message):
    if custom_message:
        return f"{custom_message}. {COMMUNITY}"
    else:
        return COMMUNITY


def function(deprecated_in, removed_in, *, name_new=None, custom_message=None):
    """A decorator for deprecated functions

    Notes
    -----
    .. versionadded:: 0.1
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            what = "deprecated" if not name_new else f"renamed to {name_new!r}"
            name_old = fn.__name__
            warnings.warn(
                f"Function {name_old!r} was "
                f"{what} in version {deprecated_in}. {name_old!r} will be "
                f"removed in version {removed_in}. {_message_end(custom_message)}",
                category=PloomberDeprecationWarning,
            )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def method(deprecated_in, removed_in, *, name_new=None, custom_message=None):
    """A decorator for deprecated methods

    Notes
    -----
    .. versionchanged:: 0.1
        Added ``name_new`` and ``custom_message``
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            what = "deprecated" if not name_new else f"renamed to {name_new!r}"
            name_old = fn.__name__
            warnings.warn(
                f"{name_old!r} from {type(self).__name__!r} was "
                f"{what} in version {deprecated_in}. {name_old!r} will be "
                f"removed in version {removed_in}. {_message_end(custom_message)}",
                category=PloomberDeprecationWarning,
            )
            return fn(self, *args, **kwargs)

        return wrapper

    return decorator
