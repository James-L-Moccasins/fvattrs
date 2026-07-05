from pathlib import Path

import pytest

from fvattrs.validators import is_file


def test_folder_raises_value_error(
    dummy_attribute: object,
    tmp_path: Path,
) -> None:
    """Given a folderpath, it must raise a ValueError."""
    with pytest.raises(ValueError, match="dummy must be a file"):
        is_file(None, dummy_attribute, tmp_path)


def test_valid_file_passes(dummy_attribute: object, tmp_path: Path) -> None:
    """Given a valid file Path, it must pass."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    is_file(None, dummy_attribute, file_path)
