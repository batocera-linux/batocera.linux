from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import InitVar, dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, Self, TypedDict, Unpack, cast

from .batoceraPaths import BATOCERA_ES_DIR, HOME, USER_ES_DIR
from .exceptions import BatoceraException
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

    if input.type == 'hat':
        return f'{keyname}:h{input.id}.{input.value}'

    if input.type == 'axis':
        if 'joystick' in input.name:
            return f"{keyname}:a{input.id}{'~' if int(input.value) > 0 else ''}"

        if keyname in ('dpup', 'dpdown', 'dpleft', 'dpright'):
            return f"{keyname}:{'-' if int(input.value) < 0 else '+'}a{input.id}"

        if 'trigger' in keyname:
            return f"{keyname}:a{input.id}{'~' if int(input.value) < 0 else ''}"

        return f'{keyname}:a{input.id}'

    if input.type == 'key':
        return None

    raise BatoceraException(f'Unknown controller input type: {input.type!r}')


def _find_input_config(roots: Iterable[ET.Element], name: str, guid: str, /) -> ET.Element:
    path = './inputConfig'

    for root in roots:
        element = root.find(f'{path}[@deviceGUID="{guid}"][@deviceName="{name}"]')
        if element is not None:
            return element

    for root in roots:
        element = root.find(f'{path}[@deviceGUID="{guid}"]')
        if element is not None:
            return element

    for root in roots:
        element = root.find(f'{path}[@deviceName="{name}"]')
        if element is not None:
            return element

    raise BatoceraException(f'Could not find controller data for "{name}" with GUID "{guid}"')


class _RelaxedDict(TypedDict):
    centered: bool
    reversed: bool


class _ControllerChanges(TypedDict, total=False):
    guid: str
    player_number: int
    index: int
    real_name: str
    device_path: str
    button_count: int
    hat_count: int
    axis_count: int
    physical_device_path: str | None
    physical_index: int | None


@dataclass(slots=True, kw_only=True)
class Controller:
    name: str
    type: Literal['keyboard', 'joystick']
    guid: str
    player_number: int  # when this is filled out, it will start at 1
    index: int
    real_name: str
    device_path: str
    button_count: int
    hat_count: int
    axis_count: int
    physical_device_path: str | None = None
    physical_index: int | None = None

    inputs_: InitVar[InputMapping | Iterable[tuple[str, Input]] | None] = None
    inputs: InputDict = field(init=False)

    def __post_init__(self, inputs_: InputMapping | Iterable[tuple[str, Input]] | None, /) -> None:
        self.inputs = dict(inputs_) if inputs_ is not None else {}

    def replace(self, /, **changes: Unpack[_ControllerChanges]) -> Self:
        return replace(self, **changes, inputs_={name: input.replace() for name, input in self.inputs.items()})

    def generate_sdl_game_db_line(self, sdl_mapping: Mapping[str, str] = _DEFAULT_SDL_MAPPING, /, ignore_buttons: list[str] | None = None) -> str:
        """Returns an SDL_GAMECONTROLLERCONFIG-formatted string for the given configuration."""
        config = [self.guid, self.real_name.replace(",", "."), "platform:Linux"]

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
            if input.name is None:  # pragma: no cover
                continue
            if ignore_buttons is not None and input.name in ignore_buttons:
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

    def get_mapping_axis_relaxed_values(self) -> dict[str, _RelaxedDict]:
        import evdev

        # read the sdl2 cache if possible for axis
        cache_file = Path(HOME / ".sdl2" / f"{self.guid}_{self.name}.cache")
        if not cache_file.exists():
            return {}

        cache_content = cache_file.read_text(encoding="utf-8").splitlines()
        n = int(cache_content[0]) # number of lines of the cache

        relaxed_values: list[int] = [int(cache_content[i]) for i in range(1, n+1)]

        # get full list of axis (in case one is not used in es)
        caps = evdev.InputDevice(self.device_path).capabilities()
        code_values: dict[int, int]  = {}
        i = 0
        for code, _ in caps[evdev.ecodes.EV_ABS]:
            if code < evdev.ecodes.ABS_HAT0X:
                code_values[code] = relaxed_values[i]
                i = i+1

        # dict with es input names
        res: dict[str, _RelaxedDict] = {}
        for x, input in self.inputs.items():
            if input.type == "axis":
                # sdl values : from -32000 to 32000 / do not put < 0 cause a wheel/pad could be not correctly centered
                # 3 possible initial positions <1----------------|-------2-------|----------------3>
                if (val := code_values.get(int(cast(str, input.code)))) is not None:
                    res[x] = { "centered":  val > -4000 and val < 4000, "reversed": val > 4000 }
                else:
                    res[x] = { "centered":  True, "reversed": False }
        return res

    # Create a controller array with the player id as a key
    @classmethod
    def load_for_players(cls, max_players: int, args: Namespace, /) -> ControllerList:
        cfg_roots = [
            ET.parse(conffile).getroot()
            for conffile in (USER_ES_DIR / 'es_input.cfg', BATOCERA_ES_DIR / 'es_input.cfg')
            if conffile.exists()
        ]

        return [
            controller
            for player_number in range(1, max_players + 1)
            if (controller := cls._find_best_controller(cfg_roots, args, player_number)) is not None
        ]

    @classmethod
    def _find_best_controller(
        cls, roots: Iterable[ET.Element], args: Namespace, player_number: int, /,
    ) -> Controller | None:
        index: int | None = getattr(args, f'p{player_number}index')

        if index is None:
            return None

        guid: str = getattr(args, f'p{player_number}guid')
        real_name: str = getattr(args, f'p{player_number}name')

        input_config = _find_input_config(roots, real_name, guid)
        return cls(
            name=cast(str, input_config.get("deviceName")),
            type=cast(Literal['keyboard', 'joystick'], input_config.get("type")),
            guid=guid,
            inputs_=Input.from_parent_element(input_config),
            player_number=player_number,
            index=index,
            real_name=real_name,
            device_path=getattr(args, f'p{player_number}devicepath'),
            button_count=getattr(args, f'p{player_number}nbbuttons'),
            hat_count=getattr(args, f'p{player_number}nbhats'),
            axis_count=getattr(args, f'p{player_number}nbaxes'),
        )

    @staticmethod
    def find_player_number(controllers: Controllers, player_number: int, /) -> Controller | None:
        for controller in controllers:
            if controller.player_number == player_number:
                return controller

        return None


def generate_sdl_game_controller_config(controllers: Controllers, /, ignore_buttons: list[str] | None = None) -> str:
    return "\n".join(controller.generate_sdl_game_db_line(ignore_buttons = ignore_buttons) for controller in controllers)


def write_sdl_controller_db(
    controllers: Controllers, outputFile: str | Path = "/tmp/gamecontrollerdb.txt", /,
) -> Path:
    outputFile = Path(outputFile)

    with outputFile.open("w") as text_file:
        text_file.write(generate_sdl_game_controller_config(controllers))

    return outputFile


type Controllers = Sequence[Controller]
type ControllerList = list[Controller]
