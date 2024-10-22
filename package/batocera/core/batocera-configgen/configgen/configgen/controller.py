from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from dataclasses import InitVar, dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, Self, TypeAlias, TypedDict, Unpack, cast

from .batoceraPaths import BATOCERA_ES_DIR, USER_ES_DIR
from .input import Input, InputDict, InputMapping

if TYPE_CHECKING:
    from argparse import Namespace


"""Default mapping of Batocera keys to SDL_GAMECONTROLLERCONFIG keys."""
_DEFAULT_SDL_MAPPING: Final = {
    'b': 'a',
    'a': 'b',
    'x': 'y',
    'y': 'x',
    'l2': 'lefttrigger',
    'r2': 'righttrigger',
    'l3': 'leftstick',
    'r3': 'rightstick',
    'pageup': 'leftshoulder',
    'pagedown': 'rightshoulder',
    'start': 'start',
    'select': 'back',
    'up': 'dpup',
    'down': 'dpdown',
    'left': 'dpleft',
    'right': 'dpright',
    'joystick1up': 'lefty',
    'joystick1left': 'leftx',
    'joystick2up': 'righty',
    'joystick2left': 'rightx',
    'hotkey': 'guide'
}


def _key_to_sdl_game_controller_config(keyname: str, input: Input, /) -> str | None:
    """
    Converts a key mapping to the SDL_GAMECONTROLLER format.

    Arguments:
      keyname: (str) SDL_GAMECONTROLLERCONFIG input name.
      input: (Input) input object.
    Returns:
      (str) SDL_GAMECONTROLLERCONFIG-formatted key mapping string.
    """
    if input.type == 'button':
        return f'{keyname}:b{input.id}'
    elif input.type == 'hat':
        return f'{keyname}:h{input.id}.{input.value}'
    elif input.type == 'axis':
        if 'joystick' in input.name:
            return f"{keyname}:a{input.id}{'~' if int(input.value) > 0 else ''}"
        elif keyname in ('dpup', 'dpdown', 'dpleft', 'dpright'):
            return f"{keyname}:{'-' if int(input.value) < 0 else '+'}a{input.id}"
        else:
            return f'{keyname}:a{input.id}'
    elif input.type == 'key':
        return None
    else:
        raise ValueError(f'unknown key type: {input.type!r}')


class _ControllerChanges(TypedDict, total=False):
    guid: str
    player_number: int
    index: int
    real_name: str
    device_path: str
    button_count: int | None
    hat_count: int | None
    axis_count: int | None
    physical_device_path: str | None
    physical_index: int | None


@dataclass(slots=True, kw_only=True)
class Controller:
    name: str
    type: Literal['keyboard', 'joystick']
    guid: str
    player_number: int = 0  # when this is filled out, it will start at 1
    index: int = -1
    real_name: str = ""
    device_path: str = ""
    button_count: int | None = None
    hat_count: int | None = None
    axis_count: int | None = None
    physical_device_path: str | None = None
    physical_index: int | None = None

    inputs_: InitVar[InputMapping | Iterable[tuple[str, Input]] | None] = None
    inputs: InputDict = field(init=False)

    def __post_init__(self, inputs_: InputMapping | Iterable[tuple[str, Input]] | None, /) -> None:
        self.inputs = dict(inputs_) if inputs_ is not None else {}

    def replace(self, /, **changes: Unpack[_ControllerChanges]) -> Self:
        return replace(self, **changes, inputs_=self.inputs)

    def generate_sdl_game_db_line(self, sdl_mapping: Mapping[str, str] = _DEFAULT_SDL_MAPPING, /) -> str:
        """Returns an SDL_GAMECONTROLLERCONFIG-formatted string for the given configuration."""
        config = [self.guid, self.real_name, "platform:Linux"]

        def add_mapping(input: Input) -> None:
            key_name = sdl_mapping.get(input.name, None)
            if key_name is None:
                return
            sdl_config = _key_to_sdl_game_controller_config(key_name, input)
            if sdl_config is not None:
                config.append(sdl_config)

        # "hotkey" is often mapped to an existing button but such a duplicate mapping
        # confuses SDL apps. We add "hotkey" mapping only if its target isn't also mapped elsewhere.
        hotkey_input: Input | None = None
        mapped_button_ids: set[str] = set()

        for input in self.inputs.values():
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
            name=cast(str, element.get("deviceName")),
            type=cast(Literal['keyboard', 'joystick'], element.get("type")),
            guid=cast(str, element.get("deviceGUID")),
            inputs_=Input.from_parent_element(element)
        )

    # Load all controllers from the es_input.cfg
    @classmethod
    def load_all(cls) -> list[Self]:
        return [
            cls.from_element(controller)
            # Parse the user's es_input.cfg first so those items are found before the system items when iterating
            for conffile in [USER_ES_DIR / 'es_input.cfg', BATOCERA_ES_DIR / "es_input.cfg"] if conffile.exists()
            for controller in ET.parse(conffile).getroot().findall(".//inputConfig")
        ]

    # Create a controller array with the player id as a key
    @classmethod
    def load_for_players(cls, max_players: int, args: Namespace, /) -> ControllerDict:
        all_controllers = cls.load_all()

        return {
            controller.player_number: controller
            for player_number in range(1, max_players + 1)
            if (controller := cls.find_best_controller_config(all_controllers, args, player_number)) is not None
        }

    @classmethod
    def find_best_controller_config(
        cls, all_controllers: Iterable[Self], args: Namespace, player_number: int, /,
    ) -> Controller | None:
        index: int | None = getattr(args, f'p{player_number}index')

        if index is None:
            return None

        guid: str = getattr(args, f'p{player_number}guid')
        real_name: str = getattr(args, f'p{player_number}name')
        device_path: str = getattr(args, f'p{player_number}devicepath')
        button_count: int = getattr(args, f'p{player_number}nbbuttons')
        hat_count: int = getattr(args, f'p{player_number}nbhats')
        axis_count: int = getattr(args, f'p{player_number}nbaxes')

        # when there will have more joysticks, use hash tables
        for controller in all_controllers:
            if controller.guid == guid and controller.name == real_name:
                return controller.replace(
                    guid=guid,
                    player_number=player_number,
                    index=index,
                    real_name=real_name,
                    device_path=device_path,
                    button_count=button_count,
                    hat_count=hat_count,
                    axis_count=axis_count,
                )

        for controller in all_controllers:
            if controller.guid == guid:
                return controller.replace(
                    guid=guid,
                    player_number=player_number,
                    index=index,
                    real_name=real_name,
                    device_path=device_path,
                    button_count=button_count,
                    hat_count=hat_count,
                    axis_count=axis_count,
                )

        for controller in all_controllers:
            if controller.name == real_name:
                return controller.replace(
                    guid=guid,
                    player_number=player_number,
                    index=index,
                    real_name=real_name,
                    device_path=device_path,
                    button_count=button_count,
                    hat_count=hat_count,
                    axis_count=axis_count,
                )

        return None


def generate_sdl_game_controller_config(controllers: ControllerMapping, /) -> str:
    return "\n".join(controller.generate_sdl_game_db_line() for controller in controllers.values())


def write_sdl_controller_db(
    controllers: ControllerMapping, outputFile: str | Path = "/tmp/gamecontrollerdb.txt", /,
) -> Path:
    outputFile = Path(outputFile)

    with outputFile.open("w") as text_file:
        text_file.write(generate_sdl_game_controller_config(controllers))

    return outputFile


ControllerMapping: TypeAlias = Mapping[int, Controller]
ControllerDict: TypeAlias = dict[int, Controller]
