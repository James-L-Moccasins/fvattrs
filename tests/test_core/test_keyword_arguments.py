import inspect

import hypothesis
import pytest

from strategies import primitives

from fvattrs import KeywordArgument


class TestIO:
    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_converter_raises(non_callable):
        with pytest.raises(TypeError):
            KeywordArgument(converter=non_callable)

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_validator_raises(non_callable):
        with pytest.raises(TypeError):
            KeywordArgument(validator=non_callable)

    @staticmethod
    @hypothesis.given(primitives.filter(lambda x: not isinstance(x, str)))
    def test_non_string_name_raises(non_string):
        with pytest.raises(TypeError):
            KeywordArgument(name=non_string)

    @staticmethod
    def test_signature():
        signature = inspect.signature(KeywordArgument.__init__)
        expected_params = [
            ("self", inspect._empty),
            ("converter", None),
            ("validator", None),
            ("name", ""),
        ]

        params = list(signature.parameters.values())
        for actual, (name, default) in zip(
            params,
            expected_params,
            strict=True,
        ):
            assert actual.name == name
            assert actual.default == default
