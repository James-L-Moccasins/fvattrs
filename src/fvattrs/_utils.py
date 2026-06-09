from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Iterator


def always_iterable(
    obj: object,
    base_type: None | tuple[type, ...] = (str, bytes),
) -> Iterator[object]:
    if obj is None:
        return iter(())

    if (base_type is not None) and isinstance(obj, base_type):
        return iter((obj,))

    try:
        return iter(obj)
    except TypeError:
        return iter((obj,))
