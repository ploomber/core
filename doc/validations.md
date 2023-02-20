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

# Validations

```{versionadded} 0.2.6
```

The `ploomber_core.validate` module makes it simple to validate user inputs and provide a meaningful message as output.

Let's say we have a function that returns a fruit from a list of fruits.

```{code-cell} ipython3
def get_fruit(fruit):
    list_of_fruits = ['apple', 'orange', 'grape']
    if fruit in list_of_fruits:
        return list_of_fruits[list_of_fruits.index(fruit)]
```

We can use it as follows:

```{code-cell} ipython3
get_fruit('apple')
```

This function works well, however, what occurs when the user requests `grapes` or makes a typo with a misspelled string such as `appel`? 
Currently, the function returns `None`. To improve input validation and provide the user with a clearer understanding of the `None` value, we may want to implement some logic.

Our `keys` validator provides us with the ability to accomplish this task. It enables us to alert the user if `grapes` are missing or there has been a typo error. Furthermore, it even allows us to suggest alternative keys as options.


```{code-cell} ipython3
from ploomber_core import validate
```

To use `keys` validator we need to pass the valid values, the input value (which can also be a sequence or a set) and the name of the parameter.

```{code-cell} ipython3
def get_fruit(fruit):
    list_of_fruits = ['apple', 'orange', 'grape']

    validate.keys(valid=list_of_fruits,
                    passed=fruit,
                    name='fruit')

    if fruit in list_of_fruits:
        return list_of_fruits[list_of_fruits.index(fruit)]
```

Now, we call the function with `grapes` as an input.

```{code-cell} ipython3
:tags: [raises-exception]

get_fruit('grapes')
```
