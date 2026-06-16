import inspect

from pathlib import Path
from typing import Callable

import hypothesis
import pytest

from strategies import primitives

from fvattrs.validators import is_file, is_folder


_VALIDATORS = pytest.mark.parametrize("validator", [is_file, is_folder])


@_VALIDATORS
class TestIO:
    """Tests the input validation of validators."""

    @staticmethod
    @hypothesis.given(primitives)
    def test_non_path_raises_type_error(
        dummy_attribute: Callable,
        validator: Callable,
        non_path: object,
    ) -> None:
        """Given a non-Path value, validators must raise a TypeError."""
        with pytest.raises(TypeError, match="dummy must be a path"):
            validator(None, dummy_attribute, non_path)

    @staticmethod
    def test_non_existent_path_raises_value_error(
        dummy_attribute: object,
        tmp_path: Path,
        validator: Callable,
    ) -> None:
        """Given a non-existent Path, validators must raise a ValueError."""
        non_existent = tmp_path / "does_not_exist.txt"
        with pytest.raises(ValueError, match=r"dummy must be a (file|folder)"):
            validator(None, dummy_attribute, non_existent)

    @staticmethod
    def test_signature(validator: Callable) -> None:
        """The signature of validators must not change."""
        signature = inspect.signature(validator)
        expected_params = [
            ("instance", inspect._empty),
            ("attribute", inspect._empty),
            ("value", inspect._empty),
        ]

        params = list(signature.parameters.values())
        for actual, (name, default) in zip(
            params,
            expected_params,
            strict=True,
        ):
            assert actual.name == name
            assert actual.default == default
