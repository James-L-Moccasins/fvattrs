import inspect

import hypothesis
import pytest

from strategies import primitives

from fvattrs import Argument


class TestIO:
    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_converter_raises(non_callable):
        with pytest.raises(TypeError):
            Argument(converter=non_callable)

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_validator_raises(non_callable):
        with pytest.raises(TypeError):
            Argument(validator=non_callable)

    @staticmethod
    @hypothesis.given(primitives.filter(lambda x: not isinstance(x, int)))
    def test_non_integer_index_raises(non_integer):
        with pytest.raises(TypeError):
            Argument(index=non_integer)

    @staticmethod
    def test_non_integer_index_raises():
        with pytest.raises(ValueError):
            Argument(index=-1)

    @staticmethod
    def test_signature():
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


def test_name_is_arg_index():
    argument = Argument(index=42)
    assert argument.name == "arg[42]"
