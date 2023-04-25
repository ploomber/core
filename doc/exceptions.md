---
jupytext:
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

# Exceptions

The `ploomber_core.exceptions` module implements some exceptions that customize the error message and add our community link at the end; the objective is to incentivize users to reach out to us when they have problems so we can assist them.

+++

## `PloomberValueError`

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

A subclass of the built-in `ValueError`, use it when the value is unexpected:

```{code-cell} ipython3
from ploomber_core import exceptions


def call_person(name="Bob"):
    if name not in {"Bob", "Alice"}:
        raise exceptions.PloomberValueError("name must be 'Bob' or 'Alice'")

    print(f"Calling {name}")
```

```{code-cell} ipython3
call_person()
```

```{code-cell} ipython3
call_person("Alice")
```

```{code-cell} ipython3
:tags: [raises-exception]

call_person("John")
```

## `PloomberTypeError`

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

A subclass of the built-in `TypeError`, use it when the type is unexpected:

```{code-cell} ipython3
from ploomber_core import exceptions # noqa


def add_one(a):
    if not isinstance(a, (int, float)):
        raise exceptions.PloomberTypeError("a must be int or float")

    return a + 1
```

```{code-cell} ipython3
add_one(1)
```

```{code-cell} ipython3
add_one(41.0)
```

```{code-cell} ipython3
:tags: [raises-exception]

add_one("hello")
```

## `PloomberKeyError`

```{versionadded} 0.1
Ensure you pin this version in the `setup.py` file (`ploomber-core>=0.1.*`)
```

A subclass of the built-in `KeyError`, use it when a key is missing:

```{code-cell} ipython3
from ploomber_core import exceptions # noqa


class MyCollection:
    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        if key not in self._data:
            raise exceptions.PloomberKeyError(f"Key {key!r} not in collection")

        return self._data[key]
```

```{code-cell} ipython3
collection = MyCollection({"a": 1})
collection["a"]
```

```{code-cell} ipython3
:tags: [raises-exception]

collection["b"]
```

## Catching generic exceptions

```{versionadded} 0.1.1
```

To catch and modify exceptions raised by third-party packages:

```{code-cell} ipython3
from ploomber_core.exceptions import modify_exceptions
```

```{code-cell} ipython3
def do_stuff():
    raise ValueError("some error")


@modify_exceptions
def some_function():
    do_stuff()
```

```{code-cell} ipython3
:tags: [raises-exception]

some_function()
```

Note that `@modify_exceptions` will only capture `ValueError` and `TypError`, if you
want other exceptions to work, you can either subclass them (preferred method)
or add the `modify_exception` attribute at runtime (this is applicable when exceptions
come from a third-party package)

```{code-cell} ipython3
class SomeThirdPartyException(Exception):
    pass

def some_third_party_call():
    raise SomeThirdPartyException("some error")


@modify_exceptions
def some_function():
    try:
        some_third_party_call()
    except Exception as e:
        e.modify_exception = True
        raise
```

```{code-cell} ipython3
:tags: [raises-exception]

some_function()
```
