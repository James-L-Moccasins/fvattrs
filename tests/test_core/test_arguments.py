import inspect

import hypothesis
import pytest

from fvattrs import PositionalArgument
from tests.strategies import primitives


class TestIO:
    """Tests the input validation of the PositionalArgument class."""

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_converter_raises(non_callable: object) -> None:
        """Given a non-callable converter, it must raise TypeError."""
        with pytest.raises(TypeError):
            PositionalArgument(converter=non_callable)

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_validator_raises(non_callable: object) -> None:
        """Given a non-callable validator, it must raise TypeError."""
        with pytest.raises(TypeError):
            PositionalArgument(validator=non_callable)

    @staticmethod
    @hypothesis.given(primitives.filter(lambda x: not isinstance(x, int)))
    def test_non_integer_index_raises(non_integer: object) -> None:
        """Given a non-integer index, it must raise TypeError."""
        with pytest.raises(TypeError):
            PositionalArgument(index=non_integer)

    @staticmethod
    def test_negative_index_raises() -> None:
        """Given a negative index, it must raise ValueError."""
        with pytest.raises(ValueError, match="'index' must be >= 0"):
            PositionalArgument(index=-1)

    @staticmethod
    def test_signature() -> None:
        """The signature of PositionalArgument must not change."""
        signature = inspect.signature(PositionalArgument.__init__)
        expected_params = [
            ("self", inspect._empty),
            ("converter", None),
            ("validator", None),
            ("index", 0),
        ]

        params = list(signature.parameters.values())
        for actual, (name, default) in zip(params, expected_params):
            assert actual.name == name
            assert actual.default == default


def test_name_is_arg_index() -> None:
    """PositionalArgument name must be 'arg[index]'."""
    assert PositionalArgument(index=42).name == "arg[42]"
