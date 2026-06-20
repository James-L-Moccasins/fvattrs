"""Utility helpers used across the package."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Iterator


def always_iterable(
    obj: object,
    base_type: None | tuple[type, ...] = (str, bytes),
) -> Iterator[object]:
    """Return an iterator for any object.

    Parameters
    ----------
    obj : object
        Object to wrap as an iterable.
    base_type : None or tuple of type, default=(str, bytes)
        Types that should be treated as a single-item iterable even when
        they are not container types.

    Returns
    -------
    collections.abc.Iterator[object]
        An iterator over the provided object.

    Note
    ----
    Code copied from more-itertools (Copyright 2012 Erik Rose) 11.1.0.

    """
    if obj is None:
        return iter(())

    if (base_type is not None) and isinstance(obj, base_type):
        return iter((obj,))

    try:
        return iter(obj)
    except TypeError:
        return iter((obj,))
