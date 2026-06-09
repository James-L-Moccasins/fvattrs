import inspect

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
    for actual, (name, default) in zip(
        params,
        expected_params,
        strict=True,
    ):
        assert actual.name == name
        assert actual.default == default

    assert signature.return_annotation == "object"


def test_interaction_with_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    """The order of execution must be converter, validator, __call__."""
    trace = []

    class MockVariable:
        def __init__(self, converter=None, validator=None):  # noqa: ANN204, ANN001  # Superfluous for mocked up class.
            trace.extend((converter, validator))
            self.converter = converter
            self.validator = validator

        def __call__(self, value):  # noqa: ANN204, ANN001  # Superfluous for mocked up class.
            trace.append(value)
            return value

    monkeypatch.setattr("fvattrs._core._Variable", MockVariable)
    value = 0
    output = define(
        value=value,
        converter="dummy_converter",
        validator="dummy_validator",
    )
    assert output == value, "Had an unexpected side effect on value."
    assert trace[0] == "dummy_converter", "converter is not called first."
    assert trace[1] == "dummy_validator", "validator is not called second."
    assert trace[2] == value, "__call__ is not called last."
