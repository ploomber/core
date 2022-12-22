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

The `deprecated` module contains utilities for marking code as deprecated.

## Deprecating method

To deprecate a method in a class, use `deprecated.method`, and pass the version where it was first deprecated and when it'll be removed.

We keep methods for two major releases. For example, if the deprecation is introduced in version `0.1`, we'll remove it in version `0.3`.

```{code-cell} ipython3
from ploomber_core import deprecated

class SomeClass:
    
    @deprecated.method(deprecated_in="0.1", removed_in="0.3")
    def do_something(self):
        return 42
```

```{code-cell} ipython3
obj = SomeClass()

# calling a deprecated method shows a warning
obj.do_something()
```
