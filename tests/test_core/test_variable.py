import inspect

import hypothesis
import pytest

from strategies import primitives

from fvattrs._core import _Variable


class TestIO:
    """Tests the input validation of _Variable."""

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_converter_raises(non_callable: object) -> None:
        """Given a non-callable converter _Variable must raise a TypeError."""
        with pytest.raises(TypeError):
            _Variable(converter=non_callable)

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_validator_raises(non_callable: object) -> None:
        """Given a non-callable validator _Variable must raise a TypeError."""
        with pytest.raises(TypeError):
            _Variable(validator=non_callable)

    @staticmethod
    def test_signature() -> None:
        """_Variable signature must not change."""
        signature = inspect.signature(_Variable.__init__)
        expected_params = [
            ("self", inspect._empty),
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
