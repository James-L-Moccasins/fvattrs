import inspect

from fvattrs import define


class TestDefine:
    @staticmethod
    def test_signature():
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

    @staticmethod
    def test_interaction_with_variable(monkeypatch):
        trace = []

        class MockVariable:
            def __init__(self, converter=None, validator=None):
                trace.extend((converter, validator))
                self.converter = converter
                self.validator = validator

            def __call__(self, value):
                trace.append(value)
                return value

        monkeypatch.setattr("fvattrs._core._Variable", MockVariable)
        value = 0
        output = define(
            value,
            converter="dummy_converter",
            validator="dummy_validator",
        )
        assert output == value, "Had an unexpected side effect on value."
        assert trace[0] == "dummy_converter", "converter is not called first."
        assert trace[1] == "dummy_validator", "validator is not called second."
        assert trace[2] == value, "__call__ is not called last."
