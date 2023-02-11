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

# Telemetry

```{versionadded} 0.1.2
Set the `_PLOOMBER_TELEMETRY_DEBUG` environment variable (any value) to override the PostHog key. Events will be logged to the "Debugging" project.
```

`ploomber-core` implements a `Telemetry` class that we use to understand usage and improve our products:

```{code-cell} ipython3
from ploomber_core.telemetry import Telemetry
```

Initialize it with the API key, name of the package, and version. Here's an example:

```{code-cell} ipython3
from ploomber_core import __version__

telemetry = Telemetry(
    api_key="SOMEKEY",
    # change for the actual name
    package_name="ploomber-core",
    # change for the actual version
    version=__version__,
)
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

To unit test decorated functions, check the `._telemetry` attribute. If it exists, it means the function has been decorated with `@log_call()`, and it'll contain the arguments passed and the action name:

```{code-cell} ipython3
assert add._telemetry == {'action': 'ploomber-core-add',
 'payload': False,
 'log_args': False,
 'ignore_args': set(),
 'group': None}
```

```{code-cell} ipython3
assert obj.add._telemetry == {'action': 'ploomber-core-add',
 'payload': False,
 'log_args': False,
 'ignore_args': set(),
 'group': None}
```

## Configuring telemetry in a package

Usually, our packages contains a `src/{package-name}/_telemetry.py` module that exposes a `telemetry` object with the key, package_name, and version already initialized. If there isn't one, create it.

Then, you can add telemetry to any module by importing the `telemetry` object.

```python
from some_package._telemetry import telemetry

@telemetry.log_call()
def some_function():
    pass
```
