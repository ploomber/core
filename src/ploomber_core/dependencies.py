from functools import wraps
import importlib


def requires(pkgs, name=None, extra_msg=None, pip_names=None):
    """
    Check if packages were imported, raise ImportError with an appropriate
    message for missing ones

    Error message:
    a, b are required to use function. Install them by running pip install a b

    Parameters
    ----------
    pkgs : list
        The names of the packages required

    name
        The name of the module/function/class to show in the error message,
        if None, the decorated function __name__ attribute is used

    extra_msg
        Append this extra message to the end

    pip_names : list
        Pip package names to show in the suggested "pip install {name}"
        command, use it if different to the package name itself

    """
    pkgs = [pkg.replace("-", "_") for pkg in pkgs]

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            is_pkg_missing = [importlib.util.find_spec(pkg) is None for pkg in pkgs]

            if any(is_pkg_missing):
                missing_pkgs = [
                    name
                    for name, is_missing in zip(pip_names or pkgs, is_pkg_missing)
                    if is_missing
                ]

                fn_name = name or f.__name__

                raise ImportError(
                    _make_requires_error_message(missing_pkgs, fn_name, extra_msg)
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator


def _make_requires_error_message(missing_pkgs, fn_name, extra_msg):
    names_str = " ".join(repr(pkg) for pkg in missing_pkgs)

    error_msg = "{} {} required to use {}. Install with: " "pip install {}".format(
        names_str,
        "is" if len(missing_pkgs) == 1 else "are",
        repr(fn_name),
        names_str,
    )

    if extra_msg:
        error_msg += "\n" + extra_msg

    return error_msg
