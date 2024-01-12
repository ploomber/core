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

# Telemetry

```{versionadded} 0.1.2
Set the `_PLOOMBER_TELEMETRY_DEBUG` environment variable (any value) to override the PostHog key. Events will be logged to the "Debugging" project.
```

`ploomber-core` implements a `Telemetry` class that we use to understand usage and improve our products:

```{code-cell} ipython3
from ploomber_core.telemetry import Telemetry
```

Initialize it with the API key, name of the package, and version. Here's an example:

```{versionadded} 0.2.20
`Telemetry.from_package`
```

```{code-cell} ipython3
telemetry = Telemetry.from_package(package_name="ploomber-core")
```

```{note}
`Telemetry.from_package` is the simplest way to initialize the telemetry object, you might use the constructor directly if you want to customize
the configuration.
```

To log call functions:

```{code-cell} ipython3
@telemetry.log_call()
def add(x, y):
    return x + y


add(1, 41)
```

Log method calls:

```{code-cell} ipython3
class MyClass:
    @telemetry.log_call()
    def add(self, x, y):
        return x, y


obj = MyClass()
obj.add(x=1, y=2)
```

```{note}
Event names are normalized by replacing underscores (`_`) with hyphens (`-`).
```

For more details, see the [API Reference](api/telemetry).

+++

## Unit testing

+++

To unit test decorated functions, call the function and check `__wrapped__._telemetry_success` attribute. If it exists, it means the function has been decorated with `@log_call()`, you can use it to verify what's logged:

```{code-cell} ipython3
@telemetry.log_call(log_args=True, ignore_args=("y",))
def divide(x, y):
    return x / y


_ = divide(2, 4)
```

```{code-cell} ipython3
from unittest.mock import ANY

assert divide.__wrapped__._telemetry_success == {
    "action": "ploomber-core-divide-success",
    "total_runtime": ANY,
    "metadata": {
        "argv": ANY,
        "args": {"x": 2},
    },
}
```

`__wrapped__._telemetry_success` will keep the latest logged data, so you must call it at least one; otherwise, it'll be `None`.

+++

## Configuring telemetry in a package

Usually, our packages contains a `src/{package-name}/_telemetry.py` module that exposes a `telemetry` object with the key, package_name, and version already initialized. If there isn't one, create it.

Then, you can add telemetry to any module by importing the `telemetry` object.

```python
from some_package._telemetry import telemetry

@telemetry.log_call()
def some_function():
    pass
```
