from collections.abc import Callable, Iterable, Mapping
from logging import Logger
from typing import Any, Final

logger: Final[Logger]

def convert(
    obj: Any,
    ids: bool,
    attr_type: bool,
    item_func: Callable[[Any], str],
    cdata: bool,
    fold_list: bool,
    parent: str = ...,
) -> str:
    """Routes the elements of an object to the right function to convert them
    based on their data type"""

def convert_dict(
    obj: Mapping[str, Any],
    ids: bool,
    parent: str,
    attr_type: bool,
    item_func: Callable[[Any], str],
    cdata: bool,
    fold_list: bool,
) -> str:
    """Converts a dict into an XML string."""

def convert_list(
    items: Iterable[Any],
    ids: bool,
    parent: str,
    attr_type: bool,
    item_func: Callable[[Any], str],
    cdata: bool,
    fold_list: bool,
) -> str:
    """Converts a list into an XML string."""

def convert_kv(key: str, val: Any, attr_type: bool, attr: dict[str, str] = ..., cdata: bool = ...) -> str:
    """Converts a number or string into an XML element"""

def convert_bool(key: str, val: Any, attr_type: bool, attr: dict[str, str] = ..., cdata: bool = ...) -> str:
    """Converts a boolean into an XML element"""

def convert_none(key: str, val: Any, attr_type: bool, attr: dict[str, str] = ..., cdata: bool = ...) -> str:
    """Converts a null value into an XML element"""
