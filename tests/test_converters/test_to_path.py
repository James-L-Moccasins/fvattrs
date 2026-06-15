from __future__ import annotations

import inspect

from os import PathLike
from pathlib import Path

import hypothesis
import pytest

from strategies import primitives

from fvattrs._converters import to_path


class TestIO:
    """Tests the input validation of `to_path`."""

    @staticmethod
    @hypothesis.given(
        primitives.filter(lambda x: not isinstance(x, (str, PathLike))),
    )
    def test_invalid_inputs_raises(invalid: object) -> None:
        """Invalid inputs must raise TypeError."""
        with pytest.raises(TypeError, match=r"to_path\(\) expects"):
            to_path(invalid)

    @staticmethod
    def test_signature() -> None:
        """The signature of `to_path` must not change."""
        signature = inspect.signature(to_path)
        expected_params = [("value", inspect._empty)]

        params = list(signature.parameters.values())
        for actual, (name, default) in zip(
            params,
            expected_params,
            strict=True,
        ):
            assert actual.name == name
            assert actual.default == default


@pytest.mark.parametrize("value", ["folder/file.txt", Path("folder/file.txt")])
def test_nominal_case_works(value: str | bytes) -> None:
    """String and bytes inputs must be converted to `Path`."""
    assert to_path(value) == Path(value)
