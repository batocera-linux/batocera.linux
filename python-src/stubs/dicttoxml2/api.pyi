from collections.abc import Callable
from logging import Logger
from typing import Any, Final

logger: Final[Logger]

def dicttoxml(
    obj: Any,
    root: bool = ...,
    custom_root: str = ...,
    ids: bool = ...,
    attr_type: bool = ...,
    item_func: Callable[[Any], str] = ...,
    cdata: bool = ...,
    fold_list: bool = ...,
) -> bytes:
    """Converts a python object into XML.
    Arguments:
    - root specifies whether the output is wrapped in an XML root element
      Default is True
    - custom_root allows you to specify a custom root element.
      Default is 'root'
    - ids specifies whether elements get unique ids.
      Default is False
    - attr_type specifies whether elements get a data type attribute.
      Default is True
    - item_func specifies what function should generate the element name for
      items in a list.
      Default is 'item'
    - cdata specifies whether string values should be wrapped in CDATA sections.
      Default is False
    - fold_list when using the option fold_list=False the parameter item_func is ignored.
      In case of nested lists, all list entries will use the same parent dictionary name as item name.
      Default is True
    """
