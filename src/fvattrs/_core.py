"""Core utilities for defining argument conversion and validation behavior."""

from __future__ import annotations

import functools
import inspect

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
from typing import Callable

import attrs

from ._utils import always_iterable


_IS_ITERABLE_OF_CALLABLE = attrs.validators.deep_iterable(
    member_validator=attrs.validators.instance_of(Callable),
)


def _to_tuple(obj: object) -> tuple[object]:
    """Normalize an object into a tuple."""
    return tuple(always_iterable(obj))


@attrs.define(frozen=True)
class _Variable:
    """Apply converters and validators to a value.

    Parameters
    ----------
    converter : callable or iterable of callables, optional
        Converter(s) applied in order to the input value.
    validator : callable or iterable of callables, optional
        Validator(s) applied to the transformed value.

    """

    name: str = attrs.field(init=False, repr=False, default="")
    converter: Callable = attrs.field(
        default=None,
        converter=_to_tuple,
        validator=_IS_ITERABLE_OF_CALLABLE,
    )
    validator: Callable = attrs.field(
        default=None,
        converter=_to_tuple,
        validator=_IS_ITERABLE_OF_CALLABLE,
    )

    def __call__(self, value: object) -> object:
        """Apply configured converters and validators to `value`.

        Parameters
        ----------
        value : object
            The value to transform and validate.

        Returns
        -------
        object
            The transformed value.

        """
        for converter in self.converter:
            value = converter(value)

        # Check if validation has been disabled in Attrs.
        if attrs.validators.get_disabled():
            return value

        for validator in self.validator:
            validator(None, self, value)

        return value


@attrs.define(frozen=True)
class PositionalArgument(_Variable):
    """Represent a positional argument in a callable signature.

    Parameters
    ----------
    index : int
        Zero-based position of the argument in the wrapped callable.
    converter : callable or iterable of callables, optional
        Converter(s) applied in order to the input value.
    validator : callable or iterable of callables, optional
        Validator(s) applied to the transformed value.

    """

    index: int = attrs.field(
        default=0,
        validator=(attrs.validators.instance_of(int), attrs.validators.ge(0)),
    )

    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, "name", f"arg[{self.index}]")


@attrs.define(frozen=True)
class KeywordArgument(_Variable):
    """Represent a keyword argument in a callable signature.

    Parameters
    ----------
    name : str
        Name of the keyword argument.
    converter : callable or iterable of callables, optional
        Converter(s) applied in order to the input value.
    validator : callable or iterable of callables, optional
        Validator(s) applied to the transformed value.

    """

    name: str = attrs.field(
        default="",
        validator=attrs.validators.instance_of(str),
    )


@attrs.define(frozen=True)
class Output(_Variable):
    """Represent the output value produced by a callable.

    Parameters
    ----------
    converter : callable or iterable of callables, optional
        Converter(s) applied in order to the input value.
    validator : callable or iterable of callables, optional
        Validator(s) applied to the transformed value.

    """

    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, "name", "output")


def define(
    value: object,
    converter: None | Callable | Iterable[Callable] = None,
    validator: None | Callable | Iterable[Callable] = None,
) -> object:
    """Apply converters and validators to a single value.

    Parameters
    ----------
    value : object
        Value to transform.
    converter : callable or iterable of callables, optional
        Converter(s) to apply.
    validator : callable or iterable of callables, optional
        Validator(s) to apply after conversion.

    Returns
    -------
    object
        The transformed value.

    """
    variable = _Variable(converter=converter, validator=validator)
    return variable(value)


def _split_parameters(
    parameters: Iterable[PositionalArgument | KeywordArgument | Output],
) -> tuple[
    tuple[PositionalArgument, ...],
    tuple[KeywordArgument, ...],
    tuple[Output, ...],
]:
    """Separate parameters into positional, keyword, and output groups."""
    arguments: list[PositionalArgument] = []
    kwarguments: list[KeywordArgument] = []
    outputs: list[Output] = []

    for parameter in parameters:
        if isinstance(parameter, PositionalArgument):
            arguments.append(parameter)
        elif isinstance(parameter, KeywordArgument):
            kwarguments.append(parameter)
        elif isinstance(parameter, Output):
            outputs.append(parameter)
        else:
            error_msg = (
                "Expected PositionalArgument | KeywordArgument | Output,"
                f" got {type(parameter)}."
            )
            raise TypeError(error_msg)

    return tuple(arguments), tuple(kwarguments), tuple(outputs)


def _preliminary_parameters_check(
    arguments: Iterable[PositionalArgument],
    kwarguments: Iterable[KeywordArgument],
    outputs: Iterable[Output],
) -> None:
    """Validate parameter combinations before signature inspection."""
    seen_indices: set[int] = set()
    for argument in arguments:
        if argument.index in seen_indices:
            error_msg = (
                f"Duplicate PositionalArgument with index {argument.index}."
            )
            raise ValueError(error_msg)
        seen_indices.add(argument.index)

    seen_names: set[str] = set()
    for kwargument in kwarguments:
        if kwargument.name in seen_names:
            error_msg = (
                f"Duplicate KeywordArgument with name {kwargument.name!r}.",
            )
            raise ValueError(error_msg)
        seen_names.add(kwargument.name)

    if len(outputs) > 1:
        error_msg = f"Expected at most one Output, got {len(outputs)}."
        raise ValueError(error_msg)


def _is_varp_or_vark(parameter: inspect.Parameter) -> bool:
    """Return whether parameter is variadic positional or keyword argument."""
    return parameter.kind in {
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
    }


def _is_positional(parameter: inspect.Parameter) -> bool:
    """Return whether parameter is positional or keyword argument."""
    return parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD


def _secondary_parameters_check(
    arguments: Iterable[PositionalArgument],
    kwarguments: Iterable[KeywordArgument],
    signature: inspect.Signature,
) -> None:
    """Validate parameter definitions against a callable signature."""
    parameters = tuple(signature.parameters.values())

    # There must be no variable arguments/keyword arguments.
    if any(filter(_is_varp_or_vark, parameters)):
        error_msg = "define_io cannot handle variable arguments."
        raise NotImplementedError(error_msg)

    # Argument index is larger than max positional argument index.
    max_index = len(tuple(filter(_is_positional, parameters))) - 1
    for argument in arguments:
        if argument.index > max_index:
            error_msg = f"index must be <= {max_index}, got {argument}"
            raise ValueError(error_msg)

    # KeywordArgument is redundant with an argument.
    names = [p.name for p in parameters if _is_positional(p)]
    kw_names = {kw.name for kw in kwarguments}
    for argument in arguments:
        name = names[argument.index]
        if name in kw_names:
            error_msg = rf"arg[{argument.index}] is redundant with {name}."
            raise ValueError(error_msg)

    # Keyword argument in missing in signature.
    names = set(signature.parameters)
    for kwargument in kwarguments:
        if (name := kwargument.name) not in names:
            error_msg = f"name must be in {names}, got {name}"
            raise ValueError(error_msg)


def define_io(
    *parameters: PositionalArgument | KeywordArgument | Output,
) -> Callable:
    """Decorate a callable to apply argument conversion and validation.

    Parameters
    ----------
    *parameters
        Positional arguments, keyword arguments, and optional output
        descriptors describing how to process the wrapped callable.

    Returns
    -------
    callable
        A decorator that wraps the target callable.

    Raises
    ------
    ValueError
        If duplicate indices, duplicate names, or multiple outputs are
        provided.
        If any argument index is invalid or conflicts with keyword names.
    NotImplementedError
        If the signature contains variable arguments or keyword arguments.

    """
    arguments, kwarguments, outputs = _split_parameters(parameters)
    _preliminary_parameters_check(arguments, kwarguments, outputs)

    def decorator(func: Callable) -> Callable:
        signature = inspect.signature(func)
        names = tuple(signature.parameters)
        _secondary_parameters_check(arguments, kwarguments, signature)

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            args, kwargs = list(args), {**kwargs}

            for variable in (*arguments, *kwarguments):
                if (index := getattr(variable, "index", None)) is not None:
                    name = names[index]
                else:
                    name = variable.name
                    index = names.index(name)

                # Named argument.
                if name in kwargs:
                    kwargs[name] = variable(kwargs[name])

                # Positional argument.
                elif (index is not None) and (0 <= index < len(args)):
                    args[index] = variable(args[index])

                # Default argument.
                elif (
                    (default := signature.parameters[name].default)
                    is not inspect._empty  # noqa: SLF001  # No other way.
                ):
                    kwargs[name] = variable(default)

                else:
                    # Safe to not test.
                    raise NotImplementedError  # pragma: no cover

            if outputs:
                return outputs[0](func(*args, **kwargs))
            return func(*args, **kwargs)

        return wrapper

    return decorator
