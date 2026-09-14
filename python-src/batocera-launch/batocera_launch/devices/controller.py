from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Container, Iterable, Mapping, Sequence
from dataclasses import InitVar, dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, Self, TypedDict, Unpack, cast

from ..exceptions import BatoceraException
from ..paths import SYSTEM_ES_DIR, USER_ES_DIR
from .input import Input, InputDict, InputMapping

if TYPE_CHECKING:
    from ..cli.arguments import PlayerArguments

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
    'hotkey': 'guide',
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
            return f'{keyname}:a{input.id}{"~" if int(input.value) > 0 else ""}'

        if keyname in ('dpup', 'dpdown', 'dpleft', 'dpright'):
            return f'{keyname}:{"-" if int(input.value) < 0 else "+"}a{input.id}'

        if 'trigger' in keyname:
            return f'{keyname}:a{input.id}{"~" if int(input.value) < 0 else ""}'

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
    physical_guid: str | None


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
    physical_guid: str | None = None

    inputs_: InitVar[InputMapping | Iterable[tuple[str, Input]] | None] = None
    inputs: InputDict = field(init=False)

    def __post_init__(self, inputs_: InputMapping | Iterable[tuple[str, Input]] | None, /) -> None:
        self.inputs = dict(inputs_) if inputs_ is not None else {}

    def replace(self, /, **changes: Unpack[_ControllerChanges]) -> Self:
        return replace(self, **changes, inputs_={name: input.replace() for name, input in self.inputs.items()})

    def generate_sdl_game_db_line(
        self, sdl_mapping: Mapping[str, str] = _DEFAULT_SDL_MAPPING, /, ignore_buttons: Container[str] | None = None
    ) -> str:
        """Returns an SDL_GAMECONTROLLERCONFIG-formatted string for the given configuration."""
        config = [self.guid, self.real_name.replace(',', '.'), 'platform:Linux']

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
            if not input.name is not None:  # pragma: no cover  # pyright: ignore[reportUnnecessaryComparison]
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

        # es wrote the cache for the physical pad, not for a virtual wheel
        device_path = self.physical_device_path or self.device_path

        try:
            input_device = evdev.InputDevice(device_path)
        except OSError:
            return {}

        # Read each axis's current value straight from the device rather than a
        # cached SDL snapshot (~/.sdl2/<guid>_<name>.cache): the cache can be
        # stale, never written yet, or captured before the device settled
        absinfo_by_code = dict(input_device.capabilities().get(evdev.ecodes.EV_ABS, []))

        # dict with es input names
        res: dict[str, _RelaxedDict] = {}
        for x, input in self.inputs.items():
            if input.type == 'axis':
                info = absinfo_by_code.get(int(cast('str', input.code)))
                if info is None or info.max == info.min:
                    res[x] = {'centered': True, 'reversed': False}
                    continue
                # 3 possible initial positions <1----------------|-------2-------|----------------3>
                frac = (info.value - info.min) / (info.max - info.min)  # 0.0 at min .. 1.0 at max
                res[x] = {'centered': 0.44 < frac < 0.56, 'reversed': frac > 0.56}
        return res

    # Create a controller array with the player id as a key
    @classmethod
    def load_for_players(cls, player_args: Iterable[PlayerArguments | None], /) -> ControllerList:
        cfg_roots = [
            ET.parse(conffile).getroot()
            for conffile in (USER_ES_DIR / 'es_input.cfg', SYSTEM_ES_DIR / 'es_input.cfg')
            if conffile.exists()
        ]

        return [
            controller
            for player_number, player_arg in enumerate(player_args, start=1)
            if player_arg is not None
            and (controller := cls._find_best_controller(cfg_roots, player_arg, player_number)) is not None
        ]

    @classmethod
    def _find_best_controller(
        cls,
        roots: Iterable[ET.Element],
        player_arg: PlayerArguments,
        player_number: int,
        /,
    ) -> Controller | None:
        input_config = _find_input_config(roots, player_arg.name, player_arg.guid)
        return cls(
            name=cast('str', input_config.get('deviceName')),
            type=cast('Literal["keyboard", "joystick"]', input_config.get('type')),
            guid=player_arg.guid,
            inputs_=Input.from_parent_element(input_config),
            player_number=player_number,
            index=player_arg.index,
            real_name=player_arg.name,
            device_path=player_arg.devicepath,
            button_count=player_arg.nbbuttons,
            hat_count=player_arg.nbhats,
            axis_count=player_arg.nbaxes,
        )

    @staticmethod
    def find_player_number(controllers: Controllers, player_number: int, /) -> Controller | None:
        for controller in controllers:
            if controller.player_number == player_number:
                return controller

        return None


def generate_sdl_game_controller_config(
    controllers: Controllers, /, ignore_buttons: Container[str] | None = None
) -> str:
    return '\n'.join(controller.generate_sdl_game_db_line(ignore_buttons=ignore_buttons) for controller in controllers)


def write_sdl_controller_db(
    controllers: Controllers,
    output_file: str | Path = '/tmp/gamecontrollerdb.txt',
    /,
) -> Path:
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open('w') as text_file:
        text_file.write(generate_sdl_game_controller_config(controllers))

    return output_file


type Controllers = Sequence[Controller]
type ControllerList = list[Controller]
