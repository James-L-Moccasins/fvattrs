from datetime import datetime
from os import PathLike
from pathlib import Path


def to_path(value: object) -> Path:
    if not isinstance(value, (str, PathLike)):
        error_msg = (
            "to_path() expects str or os.PathLike,"
            f" got {value} of type {type(value).__name__}"
        )
        raise TypeError(error_msg)
    return Path(value)


def to_date(value: object) -> datetime:
    if not isinstance(value, str):
        error_msg = (
            "to_date() expects str or datetime,"
            f" got {value} of type {type(value).__name__}",
        )
        raise TypeError(error_msg)

    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value)
