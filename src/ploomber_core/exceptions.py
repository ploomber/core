import typing as t
from click.exceptions import ClickException
from click._compat import get_text_stderr
from click.utils import echo
from gettext import gettext as _


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
        if file is None:
            file = get_text_stderr()

        echo(_(self.get_message()), file=file)


COMMUNITY = (
    "\nIf you need help solving this "
    "issue, send us a message: https://ploomber.io/community"
)


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
