from typing import Callable

import attrs
import pytest

from fvattrs._core import Argument, KeywordArgument, Output, _Variable


VARS = pytest.mark.parametrize(
    "var",
    [_Variable, Argument, KeywordArgument, Output],
)


@VARS
def test_disabling_works(
    monkeypatch: pytest.MonkeyPatch,
    dummy_validator: Callable,
    var: _Variable,
) -> None:
    """The disabling feature in attrs must work on fvattrs."""
    monkeypatch.setattr(attrs.validators, "get_disabled", lambda: True)
    var(validator=dummy_validator)(value=False)


@VARS
class TestNominalPassingCases:
    """Test cases for nominal GOOD behavior of _Variable + child classes."""

    @staticmethod
    def test_one_converter_works(
        dummy_converter: Callable,
        var: _Variable,
    ) -> None:
        """Conversion must occur."""
        assert var(converter=dummy_converter)(value=False)

    @staticmethod
    def test_many_converters_works(
        dummy_converter: Callable,
        var: _Variable,
    ) -> None:
        """All conversions must occur."""
        # ! Must have an odd number of conversion for test to work.
        converters = [dummy_converter] * 11
        assert var(converter=converters)(value=False)

    @staticmethod
    def test_passing_validator_passes(
        dummy_passing_validator: Callable,
        var: _Variable,
    ) -> None:
        """A passing validator must not raise."""
        var(validator=dummy_passing_validator)(value="toto")

    @staticmethod
    def test_validator_passes(
        dummy_validator: Callable,
        var: _Variable,
    ) -> None:
        """A valid value must pass validation."""
        var(validator=dummy_validator)(value=True)

    @staticmethod
    def test_converter_and_validator_passes(
        dummy_converter: Callable,
        dummy_validator: Callable,
        var: _Variable,
    ) -> None:
        """A converter and a validator must work together."""
        var(converter=dummy_converter, validator=dummy_validator)(value=False)


@VARS
class TestNominalRaisingCases:
    """Test cases for nominal BAD behavior of _Variable + child classes."""

    @staticmethod
    def test_validator_raises(
        dummy_validator: Callable,
        dummy_validator_exc_msg: str,
        var: _Variable,
    ) -> None:
        """A failing validator must raise the expected exception."""
        with pytest.raises(ValueError, match=dummy_validator_exc_msg):
            var(validator=dummy_validator)(value=False)

    @staticmethod
    def test_many_validator_raises(
        dummy_passing_validator: Callable,
        dummy_validator: Callable,
        dummy_validator_exc_msg: str,
        var: _Variable,
    ) -> None:
        """Multiple validators must raise the expected exception."""
        validators = (dummy_passing_validator, dummy_validator)
        with pytest.raises(ValueError, match=dummy_validator_exc_msg):
            var(validator=validators)(value=False)

    @staticmethod
    def test_attrs_validators_exception_is_explicit(var: _Variable) -> None:
        """The exception raised by attrs validators must be intact."""
        with pytest.raises(ValueError, match="must be >= 0: -1"):
            var(validator=attrs.validators.ge(0))(value=-1)
