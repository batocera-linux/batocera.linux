from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self, TypeAlias, cast

from .batoceraPaths import BATOCERA_ES_DIR, USER_ES_DIR
from .input import Input, InputDict, InputMapping

if TYPE_CHECKING:
    from argparse import Namespace

"""Default mapping of Batocera keys to SDL_GAMECONTROLLERCONFIG keys."""
_DEFAULT_SDL_MAPPING: Final = {
    'b':      'a',  'a':        'b',
    'x':      'y',  'y':        'x',
    'l2':     'lefttrigger',  'r2':    'righttrigger',
    'l3':     'leftstick',  'r3':    'rightstick',
    'pageup': 'leftshoulder', 'pagedown': 'rightshoulder',
    'start':     'start',  'select':    'back',
    'up': 'dpup', 'down': 'dpdown', 'left': 'dpleft', 'right': 'dpright',
    'joystick1up': 'lefty', 'joystick1left': 'leftx',
    'joystick2up': 'righty', 'joystick2left': 'rightx', 'hotkey': 'guide'
}


def _key_to_sdl_game_controller_config(keyname: str, name: str, type: str, id: str, value: str) -> str | None:
    """
    Converts a key mapping to the SDL_GAMECONTROLLER format.

    Arguments:
      keyname: (str) SDL_GAMECONTROLLERCONFIG input name.
      name: (str) `es_input.cfg` input name.
      type: (str) 'button', 'hat', or 'axis'
      id: (int) Numeric key id.
      value: (int) Hat value. Only used if type == 'hat' or type == 'axis' and 'joystick' in name.
    Returns:
      (str) SDL_GAMECONTROLLERCONFIG-formatted key mapping string.
    Examples:
      _keyToSdlGameControllerConfig('leftshoulder', 'l1', 'button', 6)
        'leftshoulder:b6'

      _keyToSdlGameControllerConfig('dpleft', 'left', 'hat', 0, 8)
        'dpleft:h0.8'

      _keyToSdlGameControllerConfig('lefty', 'joystick1up', 'axis', 1, -1)
        'lefty:a1'

      _keyToSdlGameControllerConfig('lefty', 'joystick1up', 'axis', 1, 1)
        'lefty:a1~'

      _keyToSdlGameControllerConfig('dpup', 'up', 'axis', 1, -1)
        'dpup:-a1'
    """
    if type == 'button':
        return f'{keyname}:b{id}'
    elif type == 'hat':
        return f'{keyname}:h{id}.{value}'
    elif type == 'axis':
        if 'joystick' in name:
            return f"{keyname}:a{id}{'~' if int(value) > 0 else ''}"
        elif keyname in ('dpup', 'dpdown', 'dpleft', 'dpright'):
            return f"{keyname}:{'-' if int(value) < 0 else '+'}a{id}"
        else:
            return f'{keyname}:a{id}'
    elif type == 'key':
        return None
    else:
        raise ValueError(f'unknown key type: {type!r}')


class Controller:
    def __init__(
        self,
        configName: str,
        type: str,
        guid: str,
        player: str | None,
        index: int | str ="-1",
        realName: str = "",
        inputs: InputMapping | Iterable[tuple[str, Input]] | None = None,
        dev: str | None = None,
        nbbuttons: int | None = None, nbhats: int | None = None, nbaxes: int | None = None
    ) -> None:
        self.type = type
        self.configName = configName
        self.index = index
        self.realName = realName
        self.guid = guid
        self.player = player
        self.dev = dev
        self.nbbuttons = nbbuttons
        self.nbhats = nbhats
        self.nbaxes = nbaxes
        self.inputs: InputDict = dict(inputs) if inputs is not None else {}

    def generate_sdl_game_db_line(self, sdlMapping: Mapping[str, str] = _DEFAULT_SDL_MAPPING, /) -> str:
        """Returns an SDL_GAMECONTROLLERCONFIG-formatted string for the given configuration."""
        config = []
        config.append(self.guid)
        config.append(self.realName)
        config.append("platform:Linux")

        def add_mapping(input: Input) -> None:
            keyname = sdlMapping.get(input.name, None)
            if keyname is None:
                return
            sdlConf = _key_to_sdl_game_controller_config(
                keyname, input.name, input.type, input.id, input.value)
            if sdlConf is not None:
                config.append(sdlConf)

        # "hotkey" is often mapped to an existing button but such a duplicate mapping
        # confuses SDL apps. We add "hotkey" mapping only if its target isn't also mapped elsewhere.
        hotkey_input = None
        mapped_button_ids = set()
        for k in self.inputs:
            input = self.inputs[k]
            if input.name is None:
                continue
            if input.name == 'hotkey':
                hotkey_input = input
                continue
            if input.type == 'button':
                mapped_button_ids.add(input.id)
            add_mapping(input)

        if hotkey_input is not None and hotkey_input.id not in mapped_button_ids:
            add_mapping(hotkey_input)
        config.append('')
        return ','.join(config)

    @classmethod
    def from_element(cls, element: ET.Element, /) -> Self:
        return cls(
            cast(str, element.get("deviceName")),
            cast(str, element.get("type")),
            cast(str, element.get("deviceGUID")),
            None,
            None,
            inputs=Input.from_parent_element(element)
        )

    # Load all controllers from the es_input.cfg
    @classmethod
    def load_all(cls) -> list[Self]:
        return [
            cls.from_element(controller)
            for conffile in [BATOCERA_ES_DIR / "es_input.cfg", USER_ES_DIR / 'es_input.cfg'] if conffile.exists()
            for controller in ET.parse(conffile).getroot().findall(".//inputConfig")
        ]

    # Create a controller array with the player id as a key
    @classmethod
    def load_for_players(cls, max_players: int, args: Namespace, /) -> ControllerDict:
        playerControllers: ControllerDict = {}
        all_controllers = cls.load_all()

        for player_number in range(1, max_players + 1):
            controller = cls.find_best_controller_config(all_controllers, args, str(player_number))
            if controller is not None:
                playerControllers[str(player_number)] = controller

        return playerControllers

    @classmethod
    def find_best_controller_config(
        cls, controllers: Iterable[Controller], args: Namespace, x: str, /,
    ) -> Controller | None:
        pxindex: int | None = getattr(args, f'p{x}index')

        if pxindex is None:
            return None

        pxguid: str = getattr(args, f'p{x}guid')
        pxname: str = getattr(args, f'p{x}name')
        pxdev: str = getattr(args, f'p{x}devicepath')
        pxnbbuttons: str = getattr(args, f'p{x}nbbuttons')
        pxnbhats: str = getattr(args, f'p{x}nbhats')
        pxnbaxes: str = getattr(args, f'p{x}nbaxes')

        # when there will have more joysticks, use hash tables
        for controller in controllers:
            if controller.guid == pxguid and controller.configName == pxname:
                return cls(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                           controller.inputs, pxdev, pxnbbuttons, pxnbhats, pxnbaxes)
        for controller in controllers:
            if controller.guid == pxguid:
                return cls(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                           controller.inputs, pxdev, pxnbbuttons, pxnbhats, pxnbaxes)
        for controller in controllers:
            if controller.configName == pxname:
                return cls(controller.configName, controller.type, pxguid, x, pxindex, pxname,
                           controller.inputs, pxdev, pxnbbuttons, pxnbhats, pxnbaxes)
        return None


def generate_sdl_game_controller_config(controllers: ControllerMapping, /) -> str:
    return "\n".join(controller.generate_sdl_game_db_line() for controller in controllers.values())


def write_sdl_controller_db(
    controllers: ControllerMapping, outputFile: str | Path = "/tmp/gamecontrollerdb.txt", /
) -> Path:
    outputFile = Path(outputFile)
    with outputFile.open("w") as text_file:
        text_file.write(generate_sdl_game_controller_config(controllers))
    return outputFile


ControllerMapping: TypeAlias = Mapping[str, Controller]
ControllerDict: TypeAlias = dict[str, Controller]
