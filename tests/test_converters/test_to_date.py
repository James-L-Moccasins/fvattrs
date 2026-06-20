from __future__ import annotations

import inspect

from datetime import datetime

import hypothesis
import pytest

from fvattrs.converters import to_date
from tests.strategies import primitives


class TestIO:
    """Tests the input validation of `to_date`."""

    @staticmethod
    @hypothesis.given(
        primitives.filter(lambda x: not isinstance(x, (str, datetime))),
    )
    def test_invalid_inputs_raises(invalid: object) -> None:
        """Invalid inputs must raise TypeError."""
        with pytest.raises(TypeError, match=r"to_date\(\) expects"):
            to_date(invalid)

    @staticmethod
    def test_signature() -> None:
        """The signature of `to_date` must not change."""
        signature = inspect.signature(to_date)
        expected_params = [("value", inspect._empty)]

        params = list(signature.parameters.values())
        for actual, (name, default) in zip(params, expected_params):
            assert actual.name == name
            assert actual.default == default


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2024-01-02T03:04:05", datetime(2024, 1, 2, 3, 4, 5)),  # noqa: DTZ001  # Ok for test.
        (datetime(2024, 1, 2, 3, 4, 5), datetime(2024, 1, 2, 3, 4, 5)),  # noqa: DTZ001  # Ok for test.
    ],
)
def test_nominal_case_works(value: str | datetime, expected: datetime) -> None:
    """Inputs must be converted to `datetime`."""
    assert to_date(value) == expected
