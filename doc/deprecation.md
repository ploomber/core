---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Deprecations

The `deprecated` module contains utilities for marking code as deprecated, renaming and changing default values.

```{important}
We keep backwards compatibility for two major releases. Example: if we're in version 0.10, we'll keep compatibility
until 0.12, if we're in 0.12.9, we'll keep it until 0.14.0
```

+++

## Function deprecated

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

```{code-cell} ipython3
from ploomber_core import deprecated

@deprecated.function(deprecated_in="0.1", removed_in="0.3")
def add(x, y):
    return x + y

add(21, 21)
```

## Function renamed

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

If the function will not disappear but be renamed, pass `name_new="new_name"`

```{code-cell} ipython3
from ploomber_core import deprecated

@deprecated.function(deprecated_in="0.1", removed_in="0.3", name_new="sum")
def add(x, y):
    return x + y

add(21, 21)
```

### Custom message

If you need to customize the message, use `custom_mesasge`:

```{code-cell} ipython3
from ploomber_core import deprecated


def sum(a, b):
    return a + b

@deprecated.function(deprecated_in="0.1", removed_in="0.3",
                     name_new="sum",
                     custom_message="Params renamed to a and b")
def add(x, y):
    return x + y

add(21, 21)
```

## Method deprecated

To deprecate a method in a class, use `deprecated.method`, and pass the version where it was first deprecated and when it'll be removed.

We keep methods for two major releases. For example, if the deprecation is introduced in version `0.1`, we'll remove it in version `0.3`.

```{code-cell} ipython3
from ploomber_core import deprecated

class SomeClass:
    
    @deprecated.method(deprecated_in="0.1", removed_in="0.3")
    def do_something(self):
        return 42

obj = SomeClass()

# calling a deprecated method shows a warning
obj.do_something()
```

## Method renamed

```{versionadded} 0.1
If using `name_new`, Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

If a method is renamed:

```{code-cell} ipython3
from ploomber_core import deprecated

class SomeClass:

    @deprecated.method(deprecated_in="0.1", removed_in="0.3", name_new="something_else")
    def do_something(self, *args, **kwargs):
        return self.do_something_else(*args, **kwargs)
    
    def do_something_else(self, a, b):
        return a + b

obj = SomeClass()
```

```{code-cell} ipython3
obj.do_something(1, 1)
```

### Custom message

If the method was renamed and any other behavior changed, use `custom_message`:

```{code-cell} ipython3
from ploomber_core import deprecated

class SomeClass:

    @deprecated.method(deprecated_in="0.1", removed_in="0.3",
                       name_new="something_else",
                       custom_message="Parameters changed from x, y to a, b")
    def do_something(self, *args, **kwargs):
        return self.do_something_else(*args, **kwargs)
    
    def do_something_else(self, a, b):
        return a + b

obj = SomeClass()
```

```{code-cell} ipython3
obj.do_something(1, 1)
```

## Attribute deprecated

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

You can use `deprecated.method` to deprecate attributes:

```{code-cell} ipython3
from ploomber_core import deprecated

class SomeClass:
    
    @property
    @deprecated.method(deprecated_in="0.1", removed_in="0.3")
    def some_attribute(self):
        return 42

obj = SomeClass()

obj.some_attribute
```

## Attribute renamed

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

If an attribute is renamed, use `deprecated.method` and pass the `renamed` argument:

```{code-cell} ipython3
from ploomber_core import deprecated

class SomeClass:
    
    @property
    @deprecated.method(deprecated_in="0.1", removed_in="0.3", name_new="new_attribute")
    def some_attribute(self):
        return self.new_attribute

    @property
    def new_attribute(self):
        return 42

obj = SomeClass()

obj.some_attribute
```

## Parameter deprecated

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

If a function/method argument is deprecated, set the default value of the old parameter to `"deprecated"` and use the following recipe:

```{code-cell} ipython3
from ploomber_core import deprecated

def example_function(k='deprecated'):
    deprecated.parameter_deprecated(deprecated_in="0.1",
                                    removed_in="0.3",
                                    name_old="k",
                                    value_passed=k)
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

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

If a parameter is renamed, set the default value of the old parameter to `"deprecated"`, set the old default value in the new parameter and:

```{code-cell} ipython3
from ploomber_core import deprecated


def example_function(n_clusters=8, k='deprecated'):
    if deprecated.parameter_renamed(deprecated_in="0.1",
                                    removed_in="0.3",
                                    name_old="k",
                                    name_new="n_clusters",
                                    value_passed=k):
        n_clusters = k
    
    print(f"k is {k!r}, n_clusters is {n_clusters!r}")

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

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

If a default value is changed, set it to `"warn"`, and:

```{code-cell} ipython3
from ploomber_core import deprecated

def example_function(n_clusters='warn'):
    value_old = 5
    if deprecated.parameter_default_changed(removed_in="0.3",
                                            name="n_clusters",
                                            value_old=value_old,
                                            value_new=10,
                                            value_passed=n_clusters):
        n_clusters = value_old
    
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

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

If the parameter is renamed and behavior changes (e.g., the default value changed), set the old parameter to `"deprecated"`, and pass a custom message:

```{code-cell} ipython3
from ploomber_core import deprecated


def example_function(n_clusters=10, k='deprecated'):
    if deprecated.parameter_renamed(deprecated_in="0.1",
                                    removed_in="0.3",
                                    name_old="k",
                                    name_new="n_clusters",
                                    value_passed=k,
                                    custom_message="Default n_clusters is 10"):
        n_clusters = k
    
    print(f"k is {k!r}, n_clusters is {n_clusters!r}")

    # ignore k and use n_clusters in the body of the function
```

```{code-cell} ipython3
example_function(k=10)
```

## Reference

This is based on [sklearn's guidelines.](https://scikit-learn.org/stable/developers/contributing.html#maintaining-backwards-compatibility)
