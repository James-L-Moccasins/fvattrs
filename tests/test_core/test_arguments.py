import inspect

import hypothesis
import pytest

from strategies import primitives

from fvattrs import Argument


class TestIO:
    """Tests the input validation of the Argument class."""

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_converter_raises(non_callable: object) -> None:
        """Given a non-callable converter, Argument must raise TypeError."""
        with pytest.raises(TypeError):
            Argument(converter=non_callable)

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_validator_raises(non_callable: object) -> None:
        """Given a non-callable validator, Argument must raise TypeError."""
        with pytest.raises(TypeError):
            Argument(validator=non_callable)

    @staticmethod
    @hypothesis.given(primitives.filter(lambda x: not isinstance(x, int)))
    def test_non_integer_index_raises(non_integer: object) -> None:
        """Given a non-integer index, Argument must raise TypeError."""
        with pytest.raises(TypeError):
            Argument(index=non_integer)

    @staticmethod
    def test_negative_index_raises() -> None:
        """Given a negative index, Argument must raise ValueError."""
        with pytest.raises(ValueError, match="'index' must be >= 0"):
            Argument(index=-1)

    @staticmethod
    def test_signature() -> None:
        """The signature of Argument must not change."""
        signature = inspect.signature(Argument.__init__)
        expected_params = [
            ("self", inspect._empty),
            ("converter", None),
            ("validator", None),
            ("index", 0),
        ]

        params = list(signature.parameters.values())
        for actual, (name, default) in zip(
            params,
            expected_params,
            strict=True,
        ):
            assert actual.name == name
            assert actual.default == default


def test_name_is_arg_index() -> None:
    """Argument name must be 'arg[index]'."""
    argument = Argument(index=42)
    assert argument.name == "arg[42]"
