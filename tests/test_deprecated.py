import pytest

from ploomber_core import deprecated
from ploomber_core.warnings import PloomberDeprecationWarning


def test_deprecated_method():
    class SomeClass:
        @deprecated.method(deprecated_in="0.10", removed_in="0.12")
        def some_method(self):
            pass

    obj = SomeClass()

    match = (
        r"'some_method' from 'SomeClass' was deprecated in version "
        r"0.10. 'some_method' will be removed in version 0.12"
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        obj.some_method()
