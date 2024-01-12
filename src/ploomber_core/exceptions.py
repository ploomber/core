import typing as t
from functools import wraps
from gettext import gettext as _

# click is an optional dependency. only available in packages that expose a CLI
try:
    from click.exceptions import ClickException
    from click._compat import get_text_stderr
    from click.utils import echo
except ModuleNotFoundError:
    ClickException = Exception
    get_text_stderr = None
    echo = None
    CLICK_AVAILABLE = False
else:
    CLICK_AVAILABLE = True

COMMUNITY_LINK = "https://ploomber.io/community"

COMMUNITY = (
    "\nIf you need help solving this " "issue, send us a message: " + COMMUNITY_LINK
)


def get_community_link():
    return COMMUNITY_LINK


def _format_message(exception):
    if hasattr(exception, "format_message"):
        return exception.format_message()
    else:
        return str(exception)


def _build_message(exception):
    msg = _format_message(exception)

    while exception.__cause__:
        msg += f"\n{_format_message(exception.__cause__)}"
        exception = exception.__cause__

    return msg


class BaseException(ClickException):
    """
    A subclass of ClickException that adds support for printing error messages
    from chained exceptions
    """

    def __init__(self, message, type_=None):
        super().__init__(message)
        self.type_ = type_

    def get_message(self):
        return f"Error: {_build_message(self)}"

    def show(self, file: t.Optional[t.IO] = None) -> None:
        if CLICK_AVAILABLE:
            if file is None:
                file = get_text_stderr()

            echo(_(self.get_message()), file=file)
        else:
            print(_(self.get_message()))


class PloomberValueError(ValueError):
    """Subclass of ValueError that displays the community link"""

    def __init__(self, message):
        super().__init__(f"{message}. {COMMUNITY}")


class PloomberTypeError(TypeError):
    """Subclass of TypeError that displays the community link"""

    def __init__(self, message):
        super().__init__(f"{message}. {COMMUNITY}")


class PloomberKeyError(KeyError):
    """Subclass of KeyError that displays the community link"""

    def __init__(self, message):
        super().__init__(f"{message}. {COMMUNITY.strip()}")


class ValidationError(BaseException):
    """Raised when failed to validate input data"""

    pass


def _add_community_link(e):
    if not len(e.args):
        e.args = (COMMUNITY,)
    elif COMMUNITY not in e.args[0]:
        message = e.args[0] + COMMUNITY
        e.args = (message,)
        # Certain exceptions like ClickException have message
        # as their first parameter. In that case args is not
        # accessed while raising the error
        if hasattr(e, "message"):
            e.message = message

    return e


def modify_exceptions(fn):
    """
    A decorator that catches ValueError, TypeError, ModifiableException and modifies
    the original error message

    Notes
    -----
    .. versionadded:: 0.1.1

    .. versionchanged:: 0.2.10
        Decorator also modifies exceptions with if they have a "modify_exception"
        attribute and it's set to True
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (ValueError, TypeError) as e:
            _add_community_link(e)
            raise

        except Exception as e:
            if getattr(e, "modify_exception", False):
                _add_community_link(e)
            raise

    return wrapper
