import inspect

import attrs
import hypothesis
import pytest

from strategies import primitives

from fvattrs import KeywordArgument, Output, PositionalArgument, define_io


class TestIO:
    """Tests the input validation of define_io."""

    @staticmethod
    def test_more_than_one_output_raises() -> None:
        """More than one output must raise a ValueError."""
        with pytest.raises(ValueError, match="Expected at most one Output"):

            @define_io(Output(), Output())
            def func() -> None:
                return None

    @staticmethod
    @hypothesis.given(primitives)
    def test_unknown_parameter_raises(primitives: object) -> None:
        """Unknown parameter types must raise a TypeError."""
        with pytest.raises(
            TypeError,
            match=(
                r"Expected PositionalArgument | KeywordArgument | Output, "
                r"got <class 'object'>."
            ),
        ):

            @define_io(primitives)
            def func() -> None:
                return None

    @staticmethod
    def test_duplicate_pos_arguments_raises() -> None:
        """Duplicate positional arguments must raise a ValueError."""
        with pytest.raises(
            ValueError,
            match="Duplicate PositionalArgument with index 0",
        ):

            @define_io(
                PositionalArgument(index=0),
                PositionalArgument(index=0),
            )
            def func() -> None:
                return None

    @staticmethod
    def test_duplicate_kwarguments_raises() -> None:
        """Duplicate keyword arguments must raise a ValueError."""
        with pytest.raises(
            ValueError,
            match="Duplicate KeywordArgument with name 'value'",
        ):

            @define_io(
                KeywordArgument(name="value"),
                KeywordArgument(name="value"),
            )
            def func() -> None:
                return None

    @staticmethod
    def test_variable_positional_argument_raises() -> None:
        """Variable positional arguments must raise a TypeError."""
        with pytest.raises(NotImplementedError):

            @define_io(PositionalArgument(index=0))
            def func(*args) -> None:
                return None

    @staticmethod
    def test_variable_keyword_argument_raises() -> None:
        """Variable keyword arguments must raise a TypeError."""
        with pytest.raises(NotImplementedError):

            @define_io(KeywordArgument(name="value"))
            def func(**kwargs) -> None:
                return None

    @staticmethod
    def test_too_large_argument_index_raises() -> None:
        """A positional argument index larger than possible must raise."""
        with pytest.raises(ValueError, match="index must be <= 0"):

            @define_io(PositionalArgument(index=1))
            def func(x) -> None:
                return None

    @staticmethod
    def test_redundant_arguments_raises() -> None:
        """A parameter defined both positionally and by name must raise."""
        with pytest.raises(ValueError):  # noqa: PT011  # regex fails wierdly.

            @define_io(
                PositionalArgument(index=0),
                KeywordArgument(name="x"),
            )
            def func(x) -> None:
                return None

    @staticmethod
    def test_missing_keyword_argument_raises() -> None:
        """A keyword argument inexistent in the function must raise."""
        with pytest.raises(
            ValueError,
            match=r"name must be in ({'x', 'y'}|{'y', 'x'})",
        ):

            @define_io(KeywordArgument(name="missing"))
            def func(x, y) -> None:
                return None

    @staticmethod
    def test_signature() -> None:
        """The signature of define_io must not change."""
        signature = inspect.signature(define_io)
        expected_param = "parameters"

        params = list(signature.parameters.values())
        assert len(params) == 1
        assert params[0].name == expected_param
        assert params[0].kind == inspect.Parameter.VAR_POSITIONAL


def e2e():
    converters = (
        lambda x: x + 1,
        lambda x: x + 2,
        lambda x: x * 3,
        lambda x: x * 4,
    )
    output_converter = lambda x: x / 2 + 1
    pos_validator = attrs.validators.gt(0)

    @define_io(
        PositionalArgument(
            index=0,
            converter=converters[0],
            validator=pos_validator,
        ),
        PositionalArgument(
            index=1,
            converter=converters[1],
            validator=pos_validator,
        ),
        KeywordArgument(
            name="z",
            converter=converters[2],
            validator=pos_validator,
        ),
        KeywordArgument(
            name="z2",
            converter=converters[3],
            validator=pos_validator,
        ),
        Output(
            converter=output_converter,
            validator=attrs.validators.lt(1e6),
        ),
    )
    def func(x: int, y: int, z: int, z2: int = 4) -> int:
        return x + y + z + z2

    def expected_function(x, y, z, z2):
        return output_converter(
            sum(
                converter(x) for converter, x in zip(converters, (x, y, z, z2))
            ),
        )

    return func, expected_function


class TestEnd2End:
    """Tests the end-to-end behavior of define_io."""

    @staticmethod
    @pytest.mark.parametrize(
        "values",
        [
            ([1, 2, 3], {"z2": 4}),  # Perfect case.
            # Unexpected named argument.
            ([1], {"z2": 4, "y": 2, "z": 3}),
            ([1, 2], {"z": 3}),  # Missing kwarg with default.
        ],
    )
    def test_conversion_works(values) -> None:
        """Decorated function must return the expected result."""
        func, expected_func = e2e()
        args, kwargs = values

        assert func(*args, **kwargs) == expected_func(1, 2, 3, 4)

    @staticmethod
    @pytest.mark.parametrize(
        "values",
        [([-1, 2, 3, 4], {}), ([1, 2, 3, -4], {}), ([1e6, 2e6, 3e6, 4e6], {})],
    )
    def test_validation_works(values) -> None:
        """Decorated function must raise ValueError."""
        func, _ = e2e()
        args, kwargs = values
        with pytest.raises(ValueError):
            func(*args, **kwargs)

    @staticmethod
    def test_empty_works() -> None:
        """Empty decorated function must return the expected result."""
        expected = 42

        @define_io()
        def func() -> int:
            return expected

        assert func() == expected
