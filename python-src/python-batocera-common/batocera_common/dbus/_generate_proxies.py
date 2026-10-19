# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import inspect
import subprocess
import textwrap
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    TypeAliasType,
    cast,
    get_args,
    get_origin,
    is_protocol,
)

from dbus_fast import SignatureTree
from dbus_fast.annotations import DBusSignature

from .interface import (
    DBusInterface,
    get_dbus_method_info,
    get_dbus_property_info,
    get_interface_name,
    iterate_dbus_methods,
    iterate_dbus_properties,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path
    from types import ModuleType


def _get_imports(annotation: Any, imports: dict[str, set[str]], /) -> None:
    args = get_args(annotation)

    for arg in args:
        _get_imports(arg, imports)

    if getattr(annotation, '__module__', None) is not None:
        module: str = annotation.__module__

        if module in ('builtins', 'inspect'):
            return

        imports[module].add(annotation.__name__)


def _split_annotation(
    annotation: object,
    location: str,
    /,
    *,
    output: bool = False,
) -> tuple[object, str]:
    if output and (annotation is None or annotation is type(None)):
        return type(None), ''

    if get_origin(annotation) is not Annotated:
        raise TypeError(f'{location}: expected Annotated[..., DBusSignature(...)]')

    python_type, *metadata = get_args(annotation)
    signatures = [item.signature for item in metadata if isinstance(item, DBusSignature)]

    if len(signatures) != 1:
        raise TypeError(f'{location}: expected exactly one DBusSignature')

    signature = signatures[0]

    try:
        tree = SignatureTree(signature)
    except Exception as error:
        raise TypeError(f'{location}: invalid D-Bus signature {signature!r}') from error

    if not tree.types or (not output and len(tree.types) != 1):
        raise TypeError(
            f'{location}: expected {"one or more output types" if output else "one complete argument type"}'
        )

    return python_type, signature


def _render_type(annotation: object, imports: set[str], /) -> str:
    if annotation is None or annotation is type(None):
        return 'None'

    if annotation is Ellipsis:
        return '...'

    if isinstance(annotation, TypeAliasType):
        imports.add(cast('str', annotation.__module__))
        return f'{annotation.__module__}.{annotation.__name__}'

    origin = get_origin(annotation)

    if origin is UnionType:
        return ' | '.join(_render_type(argument, imports) for argument in get_args(annotation))

    if origin in (list, dict, tuple, set, frozenset):
        arguments = ', '.join(_render_type(argument, imports) for argument in get_args(annotation))
        return f'{origin.__name__}[{arguments}]'

    if isinstance(annotation, type):
        if annotation.__module__ == 'builtins':
            return annotation.__qualname__

        if '<locals>' not in annotation.__qualname__:
            imports.add(annotation.__module__)
            return f'{annotation.__module__}.{annotation.__qualname__}'

    raise TypeError(f'Unsupported Python annotation: {annotation!r}')


def _generate_method(method: Callable[..., Any], imports: set[str], /) -> str:
    signature = inspect.signature(method, eval_str=True)
    parameters = list(signature.parameters.values())

    if not parameters or parameters[0].name != 'self':
        raise TypeError(f'{method.__qualname__}: expected an instance method')

    rendered_parameters = [parameters[0]]
    wire_types: list[str] = []
    argument_names: list[str] = []

    for parameter in parameters[1:]:
        location = f'{method.__qualname__}.{parameter.name}'

        if parameter.kind not in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            raise TypeError(f'{location}: expected a positional parameter')

        if parameter.default is not inspect.Parameter.empty:
            raise TypeError(f'{location}: default values are unsupported')

        python_type, wire_type = _split_annotation(
            parameter.annotation,
            location,
        )
        rendered_parameters.append(parameter.replace(annotation=_render_type(python_type, imports)))
        wire_types.append(wire_type)
        argument_names.append(parameter.name)

    python_return, wire_return = _split_annotation(
        signature.return_annotation,
        f'{method.__qualname__} return',
        output=True,
    )

    rendered_signature = signature.replace(
        parameters=rendered_parameters,
        return_annotation=_render_type(python_return, imports),
    ).format(quote_annotation_strings=False)

    method_name = get_dbus_method_info(method)['name']
    input_signature = ''.join(wire_types)
    body = ', '.join(argument_names)

    return f"""\
async def {method.__name__}{rendered_signature}:
    return await self._call_method({method_name!r}, {input_signature!r}, [{body}], {wire_return!r})
"""


def _generate_property(name: str, prop: property, imports: set[str], /) -> str:
    getter = prop.fget
    assert getter is not None

    signature = inspect.signature(getter, eval_str=True)

    python_type, wire_type = _split_annotation(
        signature.return_annotation,
        f'{getter.__qualname__} return',
    )

    rendered_type = _render_type(python_type, imports)
    wire_name = get_dbus_property_info(prop)['name']

    setter_string = ''

    if prop.fset is not None:
        setter_string = f"""\
async def set_{name}(self, value: {rendered_type}, /) -> None:
    await self._set_property({wire_name!r}, {wire_type!r}, value)
"""

    return f"""\
async def get_{name}(self) -> {rendered_type}:
    return await self._get_property({wire_name!r}, {wire_type!r})
{setter_string}"""


def _generate_proxy(interface: type[DBusInterface], imports: set[str], /) -> str:
    properties = (_generate_property(name, prop, imports) for name, prop in iterate_dbus_properties(interface))
    methods = (_generate_method(method, imports) for _, method in iterate_dbus_methods(interface))

    return f"""\
@dataclass(slots=True, frozen=True)
class {interface.__name__}Proxy(DBusProxy):
    __dbus_interface_name__: ClassVar[str] = '{get_interface_name(interface)}'

{textwrap.indent('\n'.join(properties), prefix='    ')}
{textwrap.indent('\n'.join(methods), prefix='    ')}
"""


def _get_interfaces_from_module(module: ModuleType) -> Iterator[type[DBusInterface]]:
    for attribute in vars(module).values():
        if is_protocol(attribute) and DBusInterface in attribute.__mro__ and attribute is not DBusInterface:
            yield attribute


def _get_generation_note(generation_command: str, output_file: Path | None, /) -> str:
    dbus_module_name = __name__.rsplit('.', 1)[0]
    arguments = generation_command

    if output_file is not None:
        arguments += f' {output_file}'

    return f"""\
# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

# NOTE: This file is auto-generated by `python -m {dbus_module_name} {arguments}`. Do not edit manually.
"""


def generate_proxies(
    interfaces: ModuleType, format_as: Path, header_command: str, header_output_file: Path | None, /
) -> str:
    imports: set[str] = set()

    body = '\n'.join(_generate_proxy(interface, imports) for interface in _get_interfaces_from_module(interfaces))

    imports_string = '\n'.join(f'import {module}' for module in sorted(imports)).strip()

    if imports_string:
        imports_string = f"""\
if TYPE_CHECKING:
{textwrap.indent(imports_string, prefix='    ')}

"""

    output = (
        f"""\
{_get_generation_note(header_command, header_output_file)}
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from batocera_common.dbus import DBusProxy

{imports_string}
{body}
""".strip()
        + '\n'
    )

    fixed = subprocess.run(
        ['ruff', 'check', '--select=I001', '--select=F401', '--stdin-filename', format_as, '--fix', '-'],
        input=output,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    return subprocess.run(
        ['ruff', 'format', '--quiet', '--stdin-filename', format_as, '-'],
        input=fixed,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
