from __future__ import annotations

import inspect

from collections.abc import Iterable

import hypothesis
import pytest

from fvattrs._utils import always_iterable
from tests.strategies import primitives


class TestIO:
    """Tests the input validation of `always_iterable`."""

    @staticmethod
    def test_signature() -> None:
        """The signature of `always_iterable` must not change."""
        signature = inspect.signature(always_iterable)
        expected_params = [
            ("obj", inspect._empty),
            ("base_type", (str, bytes)),
        ]

        params = list(signature.parameters.values())
        for actual, (name, default) in zip(params, expected_params):
            assert actual.name == name
            assert actual.default == default


class TestNominalCases:
    """Test cases for nominal GOOD behavior of `always_iterable`."""

    @staticmethod
    def test_none_returns_empty_iterator() -> None:
        """None must produce an empty iterable."""
        assert tuple(always_iterable(None)) == ()

    @staticmethod
    @pytest.mark.parametrize("str_like", ["abc", b"abc"])
    def test_stringlike_are_wrapped_if_in_base_type(
        str_like: str | bytes,
    ) -> None:
        """Objects in `base_type` must be wrapped."""
        assert tuple(always_iterable(str_like, base_type=(str, bytes))) == (
            str_like,
        )

    @staticmethod
    @pytest.mark.parametrize("str_like", ["abc", b"abc"])
    def test_stringlike_are_iterated_if_no_base_type(
        str_like: str | bytes,
    ) -> None:
        """Objects not in `base_type` must be iterated."""
        assert tuple(always_iterable(str_like, base_type=None)) == tuple(
            str_like,
        )

    @staticmethod
    @hypothesis.given(primitives.filter(lambda x: not isinstance(x, Iterable)))
    def test_non_iterable_returns_singleton(non_iterable: object) -> None:
        """Non-iterables must be wrapped in a singleton."""
        assert tuple(always_iterable(non_iterable)) == (non_iterable,)

    @staticmethod
    @pytest.mark.parametrize("iterable", [[1, 2, 3], (1, 2, 3), range(3)])
    def test_iterables_are_yielded_as_is(iterable: Iterable) -> None:
        """Iterables must be yielded as-is."""
        assert tuple(always_iterable(iterable)) == tuple(iterable)
