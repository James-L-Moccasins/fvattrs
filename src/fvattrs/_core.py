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
    return tuple(always_iterable(obj))


@attrs.define(frozen=True)
class _Variable:
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
    index: int = attrs.field(
        default=0,
        validator=(attrs.validators.instance_of(int), attrs.validators.ge(0)),
    )

    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, "name", f"arg[{self.index}]")


@attrs.define(frozen=True)
class KeywordArgument(_Variable):
    name: str = attrs.field(
        default="",
        validator=attrs.validators.instance_of(str),
    )


@attrs.define(frozen=True)
class Output(_Variable):
    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, "name", "output")


def define(
    value: object,
    converter: None | Callable | Iterable[Callable] = None,
    validator: None | Callable | Iterable[Callable] = None,
) -> object:
    variable = _Variable(converter=converter, validator=validator)
    return variable(value)


def _split_parameters(
    parameters: Iterable[PositionalArgument | KeywordArgument | Output],
) -> tuple[
    tuple[PositionalArgument, ...],
    tuple[KeywordArgument, ...],
    tuple[Output, ...],
]:
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
    return parameter.kind in {
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
    }


def _is_positional(parameter: inspect.Parameter) -> bool:
    return parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD


def _secondary_parameters_check(
    arguments: Iterable[PositionalArgument],
    kwarguments: Iterable[KeywordArgument],
    signature: inspect.Signature,
) -> None:
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
