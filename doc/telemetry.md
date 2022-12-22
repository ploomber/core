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

For more details, see the [API Reference](api).

## Configuring telemetry in a package

Usually, our packages contains a `src/{package-name}/_telemetry.py` module that exposes a `telemetry` object with the key, package_name, and version already initialized. If there isn't one, create it.

Then, you can add telemetry to any module by importing the `telemetry` object.

```python
from some_package._telemetry import telemetry

@telemetry.log_call()
def some_function():
    pass
```
