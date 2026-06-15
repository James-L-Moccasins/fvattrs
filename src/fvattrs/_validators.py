from pathlib import Path


def is_file(instance: object, attribute: object, value: object) -> None:  # noqa: ARG001  # Signature imposed by attrs.
    if not isinstance(value, Path):
        error_msg = f"{attribute.name} must be a path, got {value}"
        raise TypeError(error_msg)

    if not value.is_file():
        error_msg = f"{attribute.name} must be a file, got {value}"
        raise ValueError(error_msg)


def is_valid_folder(
    instance: object,  # noqa: ARG001  # Signature imposed by attrs.
    attribute: object,
    value: object,
) -> None:
    if not isinstance(value, Path):
        error_msg = f"{attribute.name} must be a path, got {value}"
        raise TypeError(error_msg)

    if not value.is_dir():
        error_msg = f"{attribute.name} must be a folder, got {value}"
        raise ValueError(error_msg)


def exists(
    instance: object,  # noqa: ARG001  # Signature imposed by attrs.
    attribute: object,
    value: object,
) -> None:
    if not isinstance(value, Path):
        error_msg = f"{attribute.name} must be a path, got {value}"
        raise TypeError(error_msg)

    if not value.exists():
        error_msg = f"{attribute.name} must exist, got {value}"
        raise ValueError(error_msg)
