---
jupytext:
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

# Optional dependencies

Often our packages contain features that require extra packages. If a feature is not regarded as core functionality, we'll make it an optional feature. This allows us to keep required dependencies at minimum, since the more dependencies we add, the higher the chance that our users will encounter problems during installation.

+++

## Example

Decorate a function witht `@requires` and pass a list of the packages.

```{code-cell} ipython3
from ploomber_core.dependencies import requires

@requires(["some_package"])
def some_optional_functionality():
    import some_package

    return x + y
```

Since `some_package` is not installed, calling the function raises an error (the function *is not* executed):

```{code-cell} ipython3
:tags: [raises-exception]

some_optional_functionality()
```

## Customizing the error message

If you need to provide more details in the error message (for example, if the package has particular installation instructions):

```{code-cell} ipython3
@requires(["some_package"], extra_msg="Some other relevant information")
def some_optional_functionality():
    import some_package

    return x + y
```

```{code-cell} ipython3
:tags: [raises-exception]

some_optional_functionality()
```

## Ensuring accurate `pip` names

Sometimes the name of the package does not match the name of the module installed. For example, you install scikit-learn with:

```sh
pip install scikit-learn
```

But import it with:

```python
import sklearn
```

In such cases, you can pass the `pip` names:

```{code-cell} ipython3
@requires(["sklean"], pip_names=["scikit-learn"])
def some_optional_functionality():
    import some_package

    return x + y
```

```{code-cell} ipython3
:tags: [raises-exception]

some_optional_functionality()
```

## Classes

Classes are supported too, decorate the `__init__` method, and pass the name of the class:

```{code-cell} ipython3
class SomeClass:
    @requires(["some_package"], name='SomeClass')
    def __init__(self):
        pass
```

```{code-cell} ipython3
:tags: [raises-exception]

obj = SomeClass()
```
