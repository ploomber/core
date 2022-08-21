import warnings
from functools import wraps

from ploomber_core.warnings import PloomberDeprecationWarning


def method(deprecated_in, removed_in):
    """A decorator for deprecated methods
    """

    def decorator(fn):

        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            warnings.warn(
                f'{fn.__name__!r} from {type(self).__name__!r} was '
                f'deprecated in version {deprecated_in} and will be '
                f'removed in version {removed_in}. Contact us if you need '
                'help migrating: https://ploomber.io/community',
                category=PloomberDeprecationWarning)
            return fn(self, *args, **kwargs)

        return wrapper

    return decorator
