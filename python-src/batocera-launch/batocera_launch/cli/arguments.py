from __future__ import annotations

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Self


@dataclass(slots=True, frozen=True)
class PlayerArguments:
    index: int
    guid: str
    name: str
    devicepath: str
    nbbuttons: int
    nbhats: int
    nbaxes: int


@dataclass(slots=True, frozen=True)
class Arguments:
    system: str
    rom: Path
    emulator: str | None
    core: str | None
    players: tuple[PlayerArguments | None, ...]
    netplaymode: str | None
    netplaypass: str | None
    netplayip: str | None
    netplayport: str | None
    netplaysession: str | None
    state_slot: str | None
    state_filename: str | None
    autosave: str | None
    systemname: str | None
    gameinfoxml: Path
    lightgun: bool
    wheel: bool
    trackball: bool
    spinner: bool

    @classmethod
    def from_namespace(cls, args: Namespace, max_players: int) -> Self:
        arguments_dict: dict[str, Any] = {}

        for field in fields(cls):
            if field.name == 'players':
                arguments_dict[field.name] = tuple(
                    None
                    if (index := getattr(args, f'p{p}index')) is None
                    or (guid := getattr(args, f'p{p}guid')) is None
                    or (name := getattr(args, f'p{p}name')) is None
                    or (devicepath := getattr(args, f'p{p}devicepath')) is None
                    or (nbbuttons := getattr(args, f'p{p}nbbuttons')) is None
                    or (nbhats := getattr(args, f'p{p}nbhats')) is None
                    or (nbaxes := getattr(args, f'p{p}nbaxes')) is None
                    else PlayerArguments(
                        index=index,
                        guid=guid,
                        name=name,
                        devicepath=devicepath,
                        nbbuttons=nbbuttons,
                        nbhats=nbhats,
                        nbaxes=nbaxes,
                    )
                    for p in range(1, max_players + 1)
                )
            else:
                arguments_dict[field.name] = getattr(args, field.name)

        return cls(**arguments_dict)

    @classmethod
    def parse(cls, max_players: int, /) -> Self:
        parser = ArgumentParser()

        for p in range(1, max_players + 1):
            parser.add_argument(f'-p{p}index', help=f'player{p} controller index', type=int, required=False)
            parser.add_argument(f'-p{p}guid', help=f'player{p} controller SDL2 guid', type=str, required=False)
            parser.add_argument(f'-p{p}name', help=f'player{p} controller name', type=str, required=False)
            parser.add_argument(f'-p{p}devicepath', help=f'player{p} controller device', type=str, required=False)
            parser.add_argument(
                f'-p{p}nbbuttons', help=f'player{p} controller number of buttons', type=int, required=False
            )
            parser.add_argument(f'-p{p}nbhats', help=f'player{p} controller number of hats', type=int, required=False)
            parser.add_argument(f'-p{p}nbaxes', help=f'player{p} controller number of axes', type=int, required=False)

        parser.add_argument('-system', help='select the system to launch', type=str, required=True)
        parser.add_argument('-rom', help='rom absolute path', type=Path, required=True)
        parser.add_argument('-emulator', help='force emulator', type=str, required=False)
        parser.add_argument('-core', help='force emulator core', type=str, required=False)
        parser.add_argument('-netplaymode', help='host/client', type=str, required=False)
        parser.add_argument('-netplaypass', help='enable spectator mode', type=str, required=False)
        parser.add_argument('-netplayip', help='remote ip', type=str, required=False)
        parser.add_argument('-netplayport', help='remote port', type=str, required=False)
        parser.add_argument('-netplaysession', help='netplay session', type=str, required=False)
        parser.add_argument('-state_slot', help='state slot', type=str, required=False)
        parser.add_argument('-state_filename', help='state filename', type=str, required=False)
        parser.add_argument('-autosave', help='autosave', type=str, required=False)
        parser.add_argument('-systemname', help='system fancy name', type=str, required=False)
        parser.add_argument(
            '-gameinfoxml', help='game info xml', type=Path, nargs='?', default=Path('/dev/null'), required=False
        )
        parser.add_argument('-lightgun', help='configure lightguns', action='store_true')
        parser.add_argument('-wheel', help='configure wheel', action='store_true')
        parser.add_argument('-trackball', help='configure trackball', action='store_true')
        parser.add_argument('-spinner', help='configure spinner', action='store_true')

        args = parser.parse_args()

        return cls.from_namespace(args, max_players)
