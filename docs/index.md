# Welcome to fvattrs

## What is fvattrs?

fvattrs helps you reduce boilerplate by having a decorator for basic conversion/validation of your function inputs/outputs. It relies heavily on [attrs](https://github.com/python-attrs/attrs).

## When to use/not use fvattrs?

Use fvattrs when you have simple validation/conversion in a function or, even more so, when you want to reuse validation/conversion helpers.

Use fvattrs when you want to standardise error message accross your code base.

Do not use fvattrs to overly validate everything; it has not been made to kill duck typing. Though you can still do so if you want :) .

Do not use fvattrs to silently convert unexpected values. Conversion should be used sparingly, cf. [Usage](https://james-l-moccasins.github.io/fvattrs/usage/) for examples.

## Installation

```bash
uv add fvattrs
```
or
```bash
pip install fvattrs
```
