from pathlib import Path
from typing import Callable

import pytest

from fvattrs.validators import is_folder


def test_file_path_raises_value_error(
    dummy_attribute: Callable,
    tmp_path: Path,
) -> None:
    """Given a Path that is a file, is_valid_folder must raise a ValueError."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    with pytest.raises(ValueError, match="dummy must be a folder"):
        is_folder(None, dummy_attribute, file_path)


def test_valid_folder_passes(
    dummy_attribute: Callable,
    tmp_path: Path,
) -> None:
    """Given a valid folder Path, is_valid_folder must pass."""
    sub_dir = tmp_path / "sub_folder"
    sub_dir.mkdir()
    is_folder(None, dummy_attribute, sub_dir)
