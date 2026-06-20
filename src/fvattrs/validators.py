"""Validators for common Python objects."""

from pathlib import Path


def is_file(instance: object, attribute: object, value: object) -> None:
    """Validate that a value points to an existing file.

    Parameters
    ----------
    instance : object
        The instance being validated.
    attribute : object
        The attribute descriptor associated with the value.
    value : object
        Candidate value. Must be a `pathlib.Path` that exists and is a file.

    Raises
    ------
    TypeError
        If `value` is not a `Path`.
    ValueError
        If `value` does not exist or is not a file.

    """
    if not isinstance(value, Path):
        error_msg = f"{attribute.name} must be a path, got {value}"
        raise TypeError(error_msg)

    if not value.is_file():
        error_msg = f"{attribute.name} must be a file, got {value}"
        raise ValueError(error_msg)


def is_folder(instance: object, attribute: object, value: object) -> None:
    """Validate that a value points to an existing directory.

    Parameters
    ----------
    instance : object
        The instance being validated.
    attribute : object
        The attribute descriptor associated with the value.
    value : object
        Candidate value. Must be a `pathlib.Path` that exists and is a
        directory.

    Raises
    ------
    TypeError
        If `value` is not a `Path`.
    ValueError
        If `value` does not exist or is not a directory.

    """
    if not isinstance(value, Path):
        error_msg = f"{attribute.name} must be a path, got {value}"
        raise TypeError(error_msg)

    if not value.is_dir():
        error_msg = f"{attribute.name} must be a folder, got {value}"
        raise ValueError(error_msg)
