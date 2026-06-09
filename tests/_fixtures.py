from typing import Any, Callable

import pytest


_DUMMY_VALIDATOR_EXC_MSG: str = "Value must be true."


def _dummy_converter(x: Any) -> bool:
    return not x


@pytest.fixture(scope="package")
def dummy_converter() -> Callable:
    return _dummy_converter


@pytest.fixture(scope="package")
def dummy_validator_exc_msg() -> str:
    return _DUMMY_VALIDATOR_EXC_MSG


def _dummy_validator(_attr: Any, instance: Any, value: Any) -> None:
    if not value:
        raise ValueError(_DUMMY_VALIDATOR_EXC_MSG)


@pytest.fixture(scope="package")
def dummy_validator() -> Callable:
    return _dummy_validator


def _dummy_passing_validator(_attr: Any, instance: Any, value: Any) -> None:
    pass


@pytest.fixture(scope="package")
def dummy_passing_validator() -> Callable:
    return _dummy_passing_validator
