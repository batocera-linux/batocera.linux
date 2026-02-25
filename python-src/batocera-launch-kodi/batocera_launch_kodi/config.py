from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Final
from xml.dom import minidom

from batocera_common.paths import HOME

if TYPE_CHECKING:
    from batocera_launch import Controllers

_KODI_USERDATA: Final = HOME / '.kodi' / 'userdata'
_HAT_POSITIONS: Final = {1: 'up', 2: 'right', 4: 'down', 8: 'left'}
_REVERSE_POSITIONS: Final = {
    'joystick1up': 'joystick1down',
    'joystick1left': 'joystick1right',
    'joystick2up': 'joystick2down',
    'joystick2left': 'joystick2right',
}
_BUTTON_MAPPING: Final = {
    'a': 'b',
    'b': 'a',
    'x': 'y',
    'y': 'x',
    'hotkey': 'guide',
    'select': 'back',
    'start': 'start',
    'pageup': 'leftbumper',
    'l2': 'lefttrigger',
    'pagedown': 'rightbumper',
    'r2': 'righttrigger',
    'up': 'up',
    'down': 'down',
    'left': 'left',
    'right': 'right',
}
_AXIS_MAPPING: Final = {
    'joystick1up': {'name': 'leftstick', 'sens': 'up'},
    'joystick1down': {'name': 'leftstick', 'sens': 'down'},
    'joystick1left': {'name': 'leftstick', 'sens': 'left'},
    'joystick1right': {'name': 'leftstick', 'sens': 'right'},
    'joystick2up': {'name': 'rightstick', 'sens': 'up'},
    'joystick2down': {'name': 'rightstick', 'sens': 'down'},
    'joystick2left': {'name': 'rightstick', 'sens': 'left'},
    'joystick2right': {'name': 'rightstick', 'sens': 'right'},
}


def _vidpid(guid: str) -> tuple[str, str]:
    return guid[10:12] + guid[8:10], guid[18:20] + guid[16:18]


def write_kodi_config(controllers: Controllers) -> None:
    # if there is no controller, don't remove the current generated one
    # it allows people to start kodi at startup when having only bluetooth joysticks
    # or this allows people to plug the last used joystick
    if not controllers:
        return

    provider = 'udev'
    buttonmap_dir = (
        _KODI_USERDATA / 'addon_data' / 'peripheral.joystick' / 'resources' / 'buttonmaps' / 'xml' / provider
    )
    buttonmap_dir.mkdir(parents=True, exist_ok=True)

    done: set[str] = set()
    for controller in controllers:
        if controller.real_name in done:
            continue
        done.add(controller.real_name)

        name_hash = hashlib.md5(controller.real_name.encode(), usedforsecurity=False).hexdigest()
        config_path = buttonmap_dir / f'batocera_{controller.guid}_{name_hash}.xml'

        document = minidom.Document()
        xml_buttonmap = document.createElement('buttonmap')
        document.appendChild(xml_buttonmap)

        xml_device = document.createElement('device')
        xml_device.setAttribute('name', controller.real_name)
        xml_device.setAttribute('provider', provider)
        if provider == 'udev':
            vid, pid = _vidpid(controller.guid)
            xml_device.setAttribute('vid', vid)
            xml_device.setAttribute('pid', pid)
        xml_device.setAttribute('buttoncount', str(controller.button_count))
        xml_device.setAttribute('axiscount', str(2 * controller.hat_count + controller.axis_count))
        xml_buttonmap.appendChild(xml_device)

        xml_controller = document.createElement('controller')
        xml_controller.setAttribute('id', 'game.controller.default')

        sticks_node: dict[str, minidom.Element] = {}
        already_set: set[str] = set()

        for controller_input in controller.inputs.values():
            if controller_input.type == 'axis' and controller_input.name in _AXIS_MAPPING:
                mapping = _AXIS_MAPPING[controller_input.name]
                if mapping['name'] not in sticks_node:
                    sticks_node[mapping['name']] = document.createElement('feature')
                    sticks_node[mapping['name']].setAttribute('name', mapping['name'])
                for sens in [controller_input.name, _REVERSE_POSITIONS[controller_input.name]]:
                    xml_sens = document.createElement(_AXIS_MAPPING[sens]['sens'])
                    val = controller_input.id
                    if (int(controller_input.value) >= 0 and sens == controller_input.name) or (
                        int(controller_input.value) < 0 and sens != controller_input.name
                    ):
                        val = f'+{val}'
                    else:
                        val = f'-{val}'
                    xml_sens.setAttribute('axis', val)
                    sticks_node[_AXIS_MAPPING[sens]['name']].appendChild(xml_sens)
            elif controller_input.name in _BUTTON_MAPPING:
                if controller_input.type == 'button':
                    btn_key = f'btn_{int(controller_input.id)}'
                    if btn_key not in already_set:
                        xml_button = document.createElement('feature')
                        xml_button.setAttribute('name', _BUTTON_MAPPING[controller_input.name])
                        xml_button.setAttribute('button', str(int(controller_input.id)))
                        xml_controller.appendChild(xml_button)
                        already_set.add(btn_key)
                elif controller_input.type == 'hat' and int(controller_input.value) in _HAT_POSITIONS:
                    xml_hat = document.createElement('feature')
                    hat_name = _HAT_POSITIONS[int(controller_input.value)]
                    val = str(controller.axis_count if hat_name in {'left', 'right'} else controller.axis_count + 1)
                    xml_hat.setAttribute('axis', f'+{val}' if hat_name in {'down', 'right'} else f'-{val}')
                    xml_hat.setAttribute('name', hat_name)
                    xml_controller.appendChild(xml_hat)
                elif controller_input.type == 'axis':
                    xml_axis = document.createElement('feature')
                    val = controller_input.id
                    val = f'+{val}' if int(controller_input.value) >= 0 else f'-{val}'
                    xml_axis.setAttribute('axis', val)
                    xml_axis.setAttribute('name', _BUTTON_MAPPING[controller_input.name])
                    xml_controller.appendChild(xml_axis)

        for node in sticks_node.values():
            xml_controller.appendChild(node)
        xml_device.appendChild(xml_controller)
        config_path.write_text(document.toprettyxml())

    settings_path = _KODI_USERDATA / 'addon_data' / 'peripheral.joystick' / 'settings.xml'
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text('<settings version="2"><setting id="driver_linux">1</setting></settings>')

    # disable the kodi splash by default (nicer integration)
    advxml = _KODI_USERDATA / 'advancedsettings.xml'
    if not advxml.exists():
        advxml.parent.mkdir(parents=True, exist_ok=True)
        advxml.write_text('<advancedsettings><splash>false</splash></advancedsettings>')
