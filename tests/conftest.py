from __future__ import annotations

import shutil

from pathlib import Path
from typing import Callable

import pytest


_DUMMY_VALIDATOR_EXC_MSG: str = "Value must be true."


def _dummy_converter(x: object) -> bool:
    return not x


@pytest.fixture(scope="package")
def dummy_converter() -> Callable:
    """Return a logical NOT converter."""
    return _dummy_converter


@pytest.fixture(scope="package")
def dummy_validator_exc_msg() -> str:
    """Return the message for dummy validator."""
    return _DUMMY_VALIDATOR_EXC_MSG


def _dummy_validator(_attr: object, instance: object, value: object) -> None:  # noqa: ARG001 # Signature imposed by attrs.
    if not value:
        raise ValueError(_DUMMY_VALIDATOR_EXC_MSG)


@pytest.fixture(scope="package")
def dummy_validator() -> Callable:
    """Return a validator that check the value is truthy."""
    return _dummy_validator


def _dummy_passing_validator(
    _attr: object,
    instance: object,
    value: object,
) -> None:
    pass


@pytest.fixture(scope="package")
def dummy_passing_validator() -> Callable:
    """Return a validator that does nothing."""
    return _dummy_passing_validator


class MockVariable:
    """A class to mock _Variable."""

    def __init__(
        self,
        converter: None | Callable = None,
        validator: None | Callable = None,
    ) -> None:
        """Initiate the instance."""
        self.trace = [converter, validator]

    def __call__(self, value: object) -> object:
        """Trace the execution and return the value as is."""
        self.trace.append(value)
        return value


@pytest.fixture(scope="package")
def mock_variable() -> Callable:
    """Return a traced MockVariable instance."""

    def factory(*args: object, **kwargs: object) -> MockVariable:
        instance = MockVariable(*args, **kwargs)
        factory.trace = instance.trace
        return instance

    factory.trace = []
    return factory


class _DummyAttribute:
    """Dummy attribute object for testing validators."""

    def __init__(self, name: str = "test_attr") -> None:
        self.name = name


@pytest.fixture(scope="package")
def dummy_attribute() -> _DummyAttribute:
    """Return a dummy attribute object for validator tests."""
    return _DummyAttribute(name="dummy")


def pytest_sessionfinish(session: object, exitstatus: int) -> None:  # noqa: ARG001  Mandatory signature.
    """Clean temp directory after pytests session ends."""
    try:
        tmp_dir = Path(session.config.rootpath) / "tmp"
    except Exception:  # noqa: BLE001  # Necessary to clean in all cases.
        return

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
