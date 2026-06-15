import inspect

import hypothesis
import pytest

from strategies import primitives

from fvattrs import KeywordArgument


class TestIO:
    """Tests the input validation of KeywordArgument."""

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_converter_raises(non_callable: object) -> None:
        """Given a non-callable converter KeywordArgument must raise a TypeError."""  # noqa: E501  # Would be less readable.
        with pytest.raises(TypeError):
            KeywordArgument(converter=non_callable)

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_callable_validator_raises(non_callable: object) -> None:
        """Given a non-callable validator KeywordArgument must raise a TypeError."""  # noqa: E501  # Would be less readable.
        with pytest.raises(TypeError):
            KeywordArgument(validator=non_callable)

    @staticmethod
    @hypothesis.given(primitives.filter(lambda x: not isinstance(x, str)))
    def test_non_string_name_raises(non_string: object) -> None:
        """Given a non-string name KeywordArgument must raise a TypeError."""
        with pytest.raises(TypeError):
            KeywordArgument(name=non_string)

    @staticmethod
    def test_signature() -> None:
        """The signature of KeywordArgument must not change."""
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
