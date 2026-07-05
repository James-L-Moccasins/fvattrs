# Usage

This page shows common `fvattrs` patterns for validation and conversion.

## 1. Validate inline using `define`

Use `define` when you have a single value and want to apply a converter and/or validator immediately (in this order).

```python
>>> import attrs
>>> from fvattrs import define
>>> value = define(42, validator=attrs.validators.ge(0))
>>> value
42
>>> 
>>> value = define(-1, validator=attrs.validators.ge(0))
Traceback (most recent call last):
  ...
ValueError: -1 is not greater than or equal to 0
```

## 2. Validate arguments in a function using `define_io`

`define_io` decorates a function to convert and/or validate arguments before the function body runs. It can
also converte/validate function output.

```python
>>> import attrs
>>> from fvattrs import define_io, PositionalArgument
>>> @define_io(
...    PositionalArgument(
...        index=0,
...        converter=int,
...        validator=attrs.validators.ge(0),
...    ),
... )
... def factorial(n):
...     result = 1
...     for i in range(2, n + 1):
...         result *= i
...     return result
>>> 
>>> print(factorial("5"))
120
```

## 3. Write a custom validator

`fvattrs` relies heavily on `attrs`, validators follow the same signature `(instance, attribute, value)` and raise `TypeError` or `ValueError` when the value is invalid. You can easily write your own validators.

```python
>>> from datetime import datetime
>>> from fvattrs import define, PositionalArgument
>>> from fvattrs.converters import to_date
>>> 
>>> def not_in_the_future(instance, attribute, value):
...     if value > datetime.now():
...         raise ValueError(f"{attribute.name} must not be in the future.")
>>> 
>>> while date := input():
...     try:
...         safe_date = define(
...             "2025-12-31",
...             converter=to_date,
...             validator=not_in_the_future,
...         )
...     except ValueError:
...         print("Please enter a valid date in the past.")
... 
...     break
```