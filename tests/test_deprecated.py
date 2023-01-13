import warnings

import pytest

from ploomber_core import deprecated
from ploomber_core.warnings import PloomberDeprecationWarning


def test_function_deprecated():
    @deprecated.function(deprecated_in="0.1", remove_in="0.3")
    def add(x, y):
        return x + y

    match = (
        "Function 'add' was deprecated in version 0.1. "
        "'add' will be removed in version 0.3"
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        add(21, 21)


def test_function_renamed():
    @deprecated.function(deprecated_in="0.1", remove_in="0.3", new_name="sum")
    def add(x, y):
        return x + y

    match = (
        "Function 'add' was renamed to 'sum' in version 0.1."
        " 'add' will be removed in version 0.3."
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        add(21, 21)


def test_function_renamed_custom_message():
    @deprecated.function(
        deprecated_in="0.1",
        remove_in="0.3",
        new_name="sum",
        custom_message="Params renamed to a and b",
    )
    def add(x, y):
        return x + y

    match = (
        "Function 'add' was renamed to 'sum' in "
        "version 0.1. 'add' will be removed in version 0.3. "
        "Params renamed to a and b"
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        add(21, 21)


def test_method_deprecated():
    class SomeClass:
        @deprecated.method(deprecated_in="0.1", remove_in="0.3")
        def do_something(self):
            return 42

    obj = SomeClass()

    match = (
        "do_something' from 'SomeClass' was deprecated in "
        "version 0.1. 'do_something' will be removed in version 0.3."
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        obj.do_something()


def test_method_renamed():
    class SomeClass:
        @deprecated.method(
            deprecated_in="0.1", remove_in="0.3", new_name="something_else"
        )
        def do_something(self, *args, **kwargs):
            return self.do_something_else(*args, **kwargs)

        def do_something_else(self, a, b):
            return a + b

    obj = SomeClass()

    match = (
        "'do_something' from 'SomeClass' was renamed to 'something_else' in "
        "version 0.1. 'do_something' will be removed in version 0.3."
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        obj.do_something(1, 1)


def test_method_renamed_custom_message():
    class SomeClass:
        @deprecated.method(
            deprecated_in="0.1",
            remove_in="0.3",
            new_name="something_else",
            custom_message="Arguments changed to a and b",
        )
        def do_something(self, *args, **kwargs):
            return self.do_something_else(*args, **kwargs)

        def do_something_else(self, a, b):
            return a + b

    obj = SomeClass()

    match = (
        "'do_something' from 'SomeClass' was renamed to 'something_else' in "
        "version 0.1. 'do_something' will be removed in version 0.3. "
        "Arguments changed to a and b"
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        obj.do_something(1, 1)


def test_attribute_deprecated():
    class SomeClass:
        @property
        @deprecated.method(deprecated_in="0.1", remove_in="0.3")
        def some_attribute(self):
            return 42

    obj = SomeClass()

    match = (
        "'some_attribute' from 'SomeClass' was deprecated in version 0.1. "
        "'some_attribute' will be removed in version 0.3."
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        obj.some_attribute


def test_attribute_renamed():
    class SomeClass:
        @property
        @deprecated.method(
            deprecated_in="0.1", remove_in="0.3", new_name="new_attribute"
        )
        def some_attribute(self):
            return self.new_attribute

        @property
        def new_attribute(self):
            return 42

    obj = SomeClass()

    match = (
        "'some_attribute' from 'SomeClass' was renamed to 'new_attribute' "
        "in version 0.1. 'some_attribute' will be removed in version 0.3."
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        obj.some_attribute


def test_parameter_deprecated():
    def example_function(k="deprecated"):
        deprecated.parameter_deprecated(
            deprecated_in="0.1", remove_in="0.3", name_old="k", value_passed=k
        )

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        example_function()

    match = "'k' was deprecated in version 0.1. 'k' will be removed in 0.3."

    with pytest.warns(PloomberDeprecationWarning, match=match):
        example_function(k=1)


def test_parameter_renamed():
    def example_function(n_clusters=8, k="deprecated"):
        n_clusters = deprecated.parameter_renamed(
            deprecated_in="0.1",
            remove_in="0.3",
            old_name="k",
            old_value=k,
            new_name="n_clusters",
            new_value=n_clusters,
        )

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        example_function()
        example_function(n_clusters=10)

    match = (
        "'k' was renamed to 'n_clusters' in version 0.1." " 'k' will be removed in 0.3."
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        example_function(k=10)


def test_parameter_new_default_value():
    def example_function(n_clusters="warn"):
        if deprecated.parameter_default_changed(
            changed_in="0.2",
            name="n_clusters",
            old_default=5,
            new_default=10,
            value=n_clusters,
        ):
            pass

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        example_function(n_clusters=3)

    match = "The default value of n_clusters will change from 5 to 10 in 0.2"

    with pytest.warns(PloomberDeprecationWarning, match=match):
        example_function()


def test_parameter_renamed_and_new_default_value():
    def example_function(n_clusters=10, k="deprecated"):
        if deprecated.parameter_renamed(
            deprecated_in="0.1",
            remove_in="0.3",
            old_name="k",
            old_value=k,
            new_name="n_clusters",
            new_value=n_clusters,
            custom_message="Default n_clusters is 10",
        ):
            pass

    match = (
        "'k' was renamed to 'n_clusters' in version 0.1. "
        "'k' will be removed in 0.3. Default n_clusters is 10."
    )

    with pytest.warns(PloomberDeprecationWarning, match=match):
        example_function(k=10)
