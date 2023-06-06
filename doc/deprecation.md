---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Deprecations

```{versionchanged} 0.2
If you use this module, ensure you pin this version in the `setup.py` file (`ploomber-core>=0.2`)
```

The `deprecated` module contains utilities for marking code as deprecated, renaming and changing default values.

```{important}
When using this module, ensure you add unit tests, click here to see [sample tests.](https://github.com/ploomber/core/blob/main/tests/test_deprecated.py)
```

```{tip}
When introducing changes, we add some directives to the docstrings, consider adding them to the tutorials that use them as well.
```

+++

## Function deprecated

To deprecate a function, use `deprecated.function`, and add the `.. deprecated::` directive:

```{code-cell} ipython3
from ploomber_core import deprecated


@deprecated.function(deprecated_in="0.1", remove_in="0.2")
def add(x, y):
    """
    Notes
    -----
    .. deprecated:: 0.1
        ``add`` is deprecated, will be removed in version 0.2
    """
    return x + y
```

When a use calls the function, a warning is displayed:

```{code-cell} ipython3
add(21, 21)
```

## Function renamed

If the function will not disappear but be renamed, pass `name_new="new_name"`.

Furthermore, add the following directives to the docstrings (with the appropriate message):

- `.. versionadded:: {deprecated_in}`: to the new function
- `.. deprecated:: {deprecated_in}`: to the old function

```{code-cell} ipython3
from ploomber_core import deprecated


def sum(x, y):
    """
    Notes
    -----
    .. versionadded:: 0.1
        ``sum`` was renamed from ``add``. ``add`` removed in version 0.2
    """
    return x + y


@deprecated.function(deprecated_in="0.1", remove_in="0.2", new_name="sum")
def add(x, y):
    """
    Notes
    -----
    .. deprecated:: 0.1
        ``add`` renamed to ``sum``. ``add`` will be removed in version 0.2
    """
    return x + y
```

Using the old function shows a warning:

```{code-cell} ipython3
add(21, 21)
```

The new one doesn't show warnings:

```{code-cell} ipython3
sum(21, 21)
```
### Custom message

If you need to customize the message, use `custom_mesasge`.

Furthermore, add the following directives to the docstrings (with the appropriate message):

- `.. versionadded:: {deprecated_in}`: to the new function (include the custom message)
- `.. deprecated:: {deprecated_in}`: to the old function

```{code-cell} ipython3
from ploomber_core import deprecated


def sum(a, b):
    """
    Notes
    -----
    .. versionadded:: 0.1
        ``sum`` was renamed from ``add``, and parameters renamed to ``a``, and ``b``.
        ``add`` removed in version 0.2
    """
    return a + b


@deprecated.function(
    deprecated_in="0.1",
    remove_in="0.3",
    new_name="sum",
    custom_message="Params renamed to a and b",
)
def add(x, y):
    """
    Notes
    -----
    .. deprecated:: 0.1
        ``add`` renamed to ``sum``. ``add`` will be removed in version 0.2
    """
    return x + y


add(21, 21)
```

## Method deprecated

To deprecate a method in a class, use `deprecated.method`, also add the `.. deprecated::` directive.

```{code-cell} ipython3
from ploomber_core import deprecated


class SomeClass:
    @deprecated.method(deprecated_in="0.1", remove_in="0.3")
    def do_something(self):
        """
        Notes
        -----
        .. deprecated:: 0.1
            ``do_something`` is deprecated, and it will be removed in version 0.2
        """
        return 42


obj = SomeClass()

# calling a deprecated method shows a warning
obj.do_something()
```

## Method renamed

If a method is renamed, use `deprecated.method`.

Furthermore, add the following directives to the docstrings (with the appropriate message):

- `.. versionadded:: {deprecated_in}`: to the new method
- `.. deprecated:: {deprecated_in}`: to the old method

```{code-cell} ipython3
from ploomber_core import deprecated


class SomeClass:
    @deprecated.method(deprecated_in="0.1", remove_in="0.2", new_name="something_else")
    def do_something(self, *args, **kwargs):
        """
        Notes
        -----
        .. deprecated:: 0.1
            ``do_something`` renamed to ``do_something_else``. ``do_something`` will
            be removed in version 0.2
        """
        return self.do_something_else(*args, **kwargs)

    def do_something_else(self, a, b):
        """
        Notes
        -----
        .. versionadded:: 0.1
            ``do_something_else`` was renamed from ``do_something``. ``do_something``
            removed in version 0.2
        """
        return a + b


obj = SomeClass()
```

```{code-cell} ipython3
obj.do_something(1, 1)
```

### Custom message

If the method was renamed and any other behavior changed, use `custom_message`.

Furthermore, add the following directives to the docstrings (with the appropriate message):

- `.. versionadded:: {deprecated_in}`: to the new method (include custom message)
- `.. deprecated:: {deprecated_in}`: to the old method

```{code-cell} ipython3
from ploomber_core import deprecated


class SomeClass:
    @deprecated.method(
        deprecated_in="0.1",
        remove_in="0.2",
        new_name="something_else",
        custom_message="Parameters changed from x, y to a, b",
    )
    def do_something(self, x, y):
        """
        Notes
        -----
        .. deprecated:: 0.1
            ``do_something`` renamed to ``do_something_else``. ``do_something``
            will be removed in version 0.2
        """
        return self.do_something_else(x, y)

    def do_something_else(self, a, b):
        """
        Notes
        -----
        .. versionadded:: 0.1
            ``do_something_else`` was renamed from ``do_something``. Parameters
            changed from x, y to a, b ``do_something`` removed in version 0.2
        """
        return a + b


obj = SomeClass()
```

```{code-cell} ipython3
obj.do_something(1, 1)
```

## Attribute deprecated

Use `deprecated.method` to deprecate attributes, and add the `.. deprecated:: {deprecated_in}` directive:

```{code-cell} ipython3
from ploomber_core import deprecated


class SomeClass:
    @property
    @deprecated.method(deprecated_in="0.1", remove_in="0.2")
    def some_attribute(self):
        """

        Notes
        -----
        .. deprecated:: 0.1
            ``some_attribute`` is deprecated, will be removed in version 0.2
        """
        return 42


obj = SomeClass()

obj.some_attribute
```

## Attribute renamed

If an attribute is renamed, use `deprecated.method` and pass the `renamed` argument.

Furthermore, add the following directives to the docstrings (with the appropriate message):

- `.. versionadded:: {deprecated_in}`: to the new attribute
- `.. deprecated:: {deprecated_in}`: to the old attribute

```{code-cell} ipython3
from ploomber_core import deprecated


class SomeClass:
    @property
    @deprecated.method(deprecated_in="0.1", remove_in="0.2", new_name="new_attribute")
    def some_attribute(self):
        """
        Notes
        -----
        .. deprecated:: 0.1
            ``some_attribute`` renamed to ``new_attribute``. ``some_attribute``
            will be removed in version 0.2
        """
        return self.new_attribute

    @property
    def new_attribute(self):
        """
        Notes
        -----
        .. versionadded:: 0.1
            ``new_attribute`` was renamed from ``some_attribute``. ``some_attribute``
            removed in version 0.2
        """
        return 42


obj = SomeClass()

obj.some_attribute
```

## Parameter deprecated

If a function/method argument is deprecated, set the default value `"deprecated"` and use the following recipe (remember to add the `.. deprecated:: {deprecated_in}` directive):

```{code-cell} ipython3
from ploomber_core import deprecated


def example_function(k="deprecated"):
    """
    Notes
    -----
    .. deprecated:: 0.1
        ``k`` argument is deprecated, will be removed in version 0.2
    """
    deprecated.parameter_deprecated(
        deprecated_in="0.1", remove_in="0.3", name_old="k", value_passed=k
    )
```

This will have no effect on calls that do not use such argument:

```{code-cell} ipython3
example_function()
```

But will warn users if they are passing such parameter:

```{code-cell} ipython3
example_function(k=1)
```

## Parameter renamed

If a parameter is renamed, follow these steps:

- Add the new parameter in the same position as the old one
- Set the old default value in the new parameter (if any)
- Move the old parameter to the end
- Set the default value of the old parameter to `"deprecated"`
- Add the `.. deprecated:: {removed_in}` directive

Then, call `deprecated.parameter_renamed`. Example:

```{code-cell} ipython3
from ploomber_core import deprecated


def example_function(n_clusters=8, another=42, k="deprecated"):
    """

    Notes
    -----
    .. deprecated:: 0.1
        ``k`` was renamed to ``n_clusters``. ``k`` removed in 0.2
    """
    n_clusters = deprecated.parameter_renamed(
        deprecated_in="0.1",
        remove_in="0.2",
        old_name="k",
        old_value=k,
        new_name="n_clusters",
        new_value=n_clusters,
    )

    print(f"n_clusters={n_clusters!r}, k={k!r}")

    # ignore k and use n_clusters in the body of the function
```

If the user is not using the deprecated parameter (`k`), no warning is shown:

```{code-cell} ipython3
example_function()
```

If a user passes the deprecated argument (`k`), a warning is displayed and the value is assigned to the new argument `n_clusters`:

```{code-cell} ipython3
example_function(k=10)
```

Once the user migrates to the new one, no warning is displayed:

```{code-cell} ipython3
example_function(n_clusters=10)
```

## Parameter with new default value

If a default value is changed, set it to `"warn"`, and use the `.. versionchanged:: {removed_in}` directive:

```{code-cell} ipython3
from ploomber_core import deprecated


def example_function(n_clusters="warn"):
    """

    Notes
    -----
    .. versionchanged:: 0.2
        'n_clusters' default value changed from 5 to 10
    """
    n_clusters = deprecated.parameter_default_changed(
        "0.2", name="n_clusters", old_default=5, new_default=10, value=n_clusters
    )

    print(f"n_clusters is {n_clusters}")
```

Functions that do not rely on the default value won't show any warning:

```{code-cell} ipython3
example_function(n_clusters=3)
```

But if a user relies on the default value, the old default value is used but a warning is shown:

```{code-cell} ipython3
example_function()
```

## Parameter renamed and changed


If the parameter is renamed and behavior changes:

- Add the new parameter in the same position as the old one
- Set the old default value in the new parameter (if any)
- Move the old parameter to the end
- Set the default value of the old parameter to `"deprecated"`
- Add the `.. deprecated:: {removed_in}` directive
- Include a message with the new default

```{code-cell} ipython3
from ploomber_core import deprecated


def example_function(n_clusters=10, another=42, k="deprecated"):
    """

    Notes
    -----
    .. deprecated:: 0.1
        ``k`` was renamed to ``n_clusters``. ``k`` removed in 0.2. Default n_clusters
        is 10
    """
    n_clusters = deprecated.parameter_renamed(
        "0.1",
        "0.2",
        old_name="k",
        old_value=k,
        new_name="n_clusters",
        new_value=n_clusters,
        custom_message="Default n_clusters is 10",
    )

    print(f"n_clusters={n_clusters!r}, k={k!r}")

    # ignore k and use n_clusters in the body of the function
```

```{code-cell} ipython3
example_function(k=10)
```

## Deprecation warning with logger

`deprecation_warning(telemetry, message)` is designed to facilitate the logging of deprecated features in your codebase. It throws warning messages and log
the information about the message, the current package name and version.

We need to provide telemetry instance and the message string:

- telemetry, [Telemetry class](https://ploomber-core--65.org.readthedocs.build/en/65/telemetry.html)
- message, str, the message to display

### Example

In the [jupysql](https://github.com/ploomber/jupysql) project, we may import the existing telemetry instance and pass to `deprecation_warning`

```
from sql.telemetry import telemetry

def some_random_func():
    deprecation_warning(telemetry, "you are using old feature")

some_random_func()
```

The message `you are using old feature` and jupysql package info will be logged

## Reference

This is based on [sklearn's guidelines.](https://scikit-learn.org/stable/developers/contributing.html#maintaining-backwards-compatibility)
