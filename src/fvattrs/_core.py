from __future__ import annotations

import functools

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
class Argument(_Variable):
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
    parameters: Iterable[Argument | KeywordArgument],
) -> tuple[tuple[Argument, ...], tuple[KeywordArgument, ...]]:
    arguments: list[Argument] = []
    kwarguments: list[KeywordArgument] = []
    outputs: list[Output] = []

    for parameter in parameters:
        if isinstance(parameter, Argument):
            arguments.append(parameter)
        elif isinstance(parameter, KeywordArgument):
            kwarguments.append(parameter)
        elif isinstance(parameter, Output):
            outputs.append(parameter)
        else:
            error_msg = (
                "Expected Argument | KeywordArgument | Output,"
                f" got {type(parameter)}."
            )
            raise TypeError(error_msg)

    return tuple(arguments), tuple(kwarguments), tuple(outputs)


def define_io(*parameters: Argument | KeywordArgument | Output) -> Callable:
    arguments, kwarguments, outputs = _split_parameters(parameters)

    if len(outputs) > 1:
        error_msg = f"Expected at most one Output, got {len(outputs)}."
        raise ValueError(error_msg)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            for argument in arguments:
                args = list(args)
                args[argument.index] = argument(args[argument.index])

            for kwargument in kwarguments:
                kwargs[kwargument.name] = kwargument(kwargs[kwargument.name])

            if outputs:
                raw_output = func(*args, **kwargs)
                return outputs[0](raw_output)

            return func(*args, **kwargs)

        return wrapper

    return decorator
