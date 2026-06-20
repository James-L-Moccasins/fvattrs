"""Converters for common Python types."""

from datetime import datetime
from os import PathLike
from pathlib import Path


def to_path(value: object) -> Path:
    """Convert a value to a filesystem path.

    Parameters
    ----------
    value : object
        Value to convert. Must be a string or any object accepted by
        `os.PathLike`.

    Returns
    -------
    pathlib.Path
        A `Path` instance created from `value`.

    Raises
    ------
    TypeError
        If `value` is not a string or path-like object.

    """
    if not isinstance(value, (str, PathLike)):
        error_msg = (
            "to_path() expects str or os.PathLike,"
            f" got {value} of type {type(value).__name__}"
        )
        raise TypeError(error_msg)
    return Path(value)


def to_date(value: object) -> datetime:
    """Convert a value to a `datetime` object.

    Parameters
    ----------
    value : object
        Value to convert. If this is already a `datetime`, it is returned
        unchanged. Otherwise, it must be a string in ISO 8601 format.

    Returns
    -------
    datetime.datetime
        Parsed datetime value.

    Raises
    ------
    TypeError
        If `value` is neither a string nor a `datetime`.
    ValueError
        If `value` is a string that cannot be parsed by
        `datetime.fromisoformat`.

    """
    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        error_msg = (
            "to_date() expects str or datetime,"
            f" got {value} of type {type(value).__name__}",
        )
        raise TypeError(error_msg)

    return datetime.fromisoformat(value)
