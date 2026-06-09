import attrs
import pytest

from fvattrs._core import Argument, KeywordArgument, Output, _Variable


VARS = pytest.mark.parametrize(
    "var",
    [_Variable, Argument, KeywordArgument, Output],
)


@VARS
def test_disabling_works(monkeypatch, dummy_validator, var):
    monkeypatch.setattr(attrs.validators, "get_disabled", lambda: True)
    var(validator=dummy_validator)(False)


@VARS
class TestNominalPassingCases:
    @staticmethod
    def test_one_converter_works(dummy_converter, var):
        assert var(converter=dummy_converter)(False)

    @staticmethod
    def test_many_converters_works(dummy_converter, var):
        # ! Must have an odd number of conversion for test to work.
        converters = [dummy_converter] * 11
        assert var(converter=converters)(False)

    @staticmethod
    def test_passing_validator_passes(dummy_passing_validator, var):
        var(validator=dummy_passing_validator)("toto")

    @staticmethod
    def test_validator_passes(dummy_validator, var):
        var(validator=dummy_validator)(True)

    @staticmethod
    def test_converter_and_validator_passes(
        dummy_converter,
        dummy_validator,
        var,
    ):
        var(converter=dummy_converter, validator=dummy_validator)(False)


@VARS
class TestNominalRaisingCases:
    @staticmethod
    def test_validator_raises(dummy_validator, dummy_validator_exc_msg, var):
        with pytest.raises(ValueError, match=dummy_validator_exc_msg):
            var(validator=dummy_validator)(False)

    @staticmethod
    def test_many_validator_raises(
        dummy_passing_validator,
        dummy_validator,
        dummy_validator_exc_msg,
        var,
    ):
        validators = (dummy_passing_validator, dummy_validator)
        with pytest.raises(ValueError, match=dummy_validator_exc_msg):
            var(validator=validators)(False)

    @staticmethod
    def test_attrs_validators_exception_is_explicit(var):
        with pytest.raises(ValueError, match="must be >= 0: -1"):
            var(validator=attrs.validators.ge(0))(-1)
