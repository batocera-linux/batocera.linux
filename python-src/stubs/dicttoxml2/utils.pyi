from collections.abc import Mapping
from logging import Logger
from typing import Any, Final, Literal, LiteralString

logger: Final[Logger]

def set_debug(debug: bool = ..., filename: str = ...) -> None:
    """Kept for BC reasons."""

def make_id(element: object, start: int = ..., end: int = ...) -> str:
    """Returns a random integer. Kept for BC reasons."""

def get_unique_id(element: object) -> str:
    """Returns a unique id for a given element"""

def get_xml_type(val: object) -> str:
    """Returns the data type for the xml type attribute"""

def escape_xml(s: str) -> str:
    """Kept for BC reasons"""

def make_attrstring(attr: Mapping[Any, Any]) -> LiteralString:
    """Returns an attribute string in the form key="val" """

def key_is_valid_xml(key: object) -> bool:
    """Checks that a key is a valid XML name"""

def make_valid_xml_name(
    key: str, attr: dict[str, str]
) -> tuple[str, dict[str, str]] | tuple[Literal['key'], dict[str, str]]:
    """Tests an XML name and fixes it if invalid"""

def wrap_cdata(s: object) -> str:
    """Wraps a string into CDATA sections"""

def default_item_func(parent: object) -> str: ...
