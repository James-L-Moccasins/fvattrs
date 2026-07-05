import inspect

from collections.abc import Callable

import pytest

from fvattrs import define


def test_signature() -> None:
    """The signature of define must not change."""
    signature = inspect.signature(define)
    expected_params = [
        ("value", inspect._empty),
        ("converter", None),
        ("validator", None),
    ]

    params = list(signature.parameters.values())
    for actual, (name, default) in zip(params, expected_params):
        assert actual.name == name
        assert actual.default == default

    assert signature.return_annotation == "object"


def test_interaction_with_variable(
    monkeypatch: pytest.MonkeyPatch,
    mock_variable: Callable,
) -> None:
    """The order of execution must be converter, validator, __call__."""
    monkeypatch.setattr("fvattrs._core._Variable", mock_variable)

    value = 0
    output = define(
        value=value,
        converter="dummy_converter",
        validator="dummy_validator",
    )

    assert output == value
    assert mock_variable.trace == ["dummy_converter", "dummy_validator", value]
