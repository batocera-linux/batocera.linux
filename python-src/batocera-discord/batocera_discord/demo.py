"""Renders the panel with sample data, for documentation screenshots and visual checks."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, Any

from . import paths
from .controls import Action, Family
from .i18n import _
from .state import AudioDevices, Call, Phase, State

if TYPE_CHECKING:
    from pathlib import Path


class DemoController:
    def __init__(self) -> None:
        self.state = State()
        self.current_family = Family.XBOX
        self.setup_link: str | None = None

    def family(self) -> Family:
        return self.current_family

    def image_path(self, key: str, /) -> Path:
        return paths.CACHE_DIR / f'{key}.png'

    def setup_url(self) -> str | None:
        return self.setup_link

    def recents(self) -> list[dict[str, str]]:
        return [
            {'name': 'Glenn', 'channel_id': '100000000000000001'},
            {'name': 'Kyro, Magerius', 'channel_id': '100000000000000002'},
        ]

    def install_discord(self) -> None: ...
    def show_discord_window(self) -> None: ...
    def close_overlay(self) -> None: ...
    def load_channels(self, guild_id: str, /) -> None: ...
    def join(self, channel_id: str, /) -> None: ...
    def leave(self) -> None: ...
    def toggle_mute(self) -> None: ...
    def toggle_deaf(self) -> None: ...
    def set_user_volume(self, user_id: str, volume: int, /) -> None: ...
    def set_user_mute(self, user_id: str, mute: bool, /) -> None: ...
    def logout(self) -> None: ...


def _sample(state: State, /) -> None:
    me: dict[str, Any] = {'id': '1', 'username': 'player', 'global_name': 'Player One'}
    friends: list[dict[str, Any]] = [
        {'id': str(10 + i), 'username': name.lower(), 'global_name': name}
        for i, name in enumerate(('Glenn', 'Kyro', 'Magerius', 'Ghzwn', 'Lia'))
    ]
    state.phase = Phase.READY
    state.user = me
    state.guilds = [
        {'id': str(1000 + i), 'name': name}
        for i, name in enumerate(('Retro Night', 'Mario Kart Club', 'Speedrunners FR', 'Arcade Legends'))
    ]
    state.channels['1000'] = [
        {'id': '2001', 'name': 'General', 'type': 2, 'voice_states': [{'user': friends[0]}, {'user': friends[1]}]},
        {'id': '2002', 'name': 'Ranked', 'type': 2, 'voice_states': [{'user': f} for f in friends]},
        {'id': '2003', 'name': 'AFK', 'type': 2, 'voice_states': []},
    ]
    state.call = Call('2001', 'General', 2, '1000', time.time() - 754)
    state.members = {
        '1': {'user': me, 'voice_state': {}},
        '10': {'user': friends[0], 'volume': 120, 'voice_state': {}},
        '11': {'user': friends[1], 'volume': 80, 'voice_state': {'self_mute': True}},
        '12': {'user': friends[2], 'volume': 100, 'voice_state': {'self_deaf': True}, 'nick': 'Mage'},
    }
    state.speaking = {'10'}
    state.audio = AudioDevices(mic='USB Headset', output='USB Headset')


def render_demo(directory: Path, language: str = 'en', /) -> int:
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    import pygame

    from .ui.overlay import PANEL_WIDTH, Overlay

    try:
        pygame.display.init()
    except pygame.error:
        # Batocera's SDL has no dummy driver: use a 1x1 X11 window placed outside the screen
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['SDL_X11_FORCE_OVERRIDE_REDIRECT'] = '1'
        os.environ['SDL_VIDEO_WINDOW_POS'] = '6000,6000'
        pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    _.set_language(language)
    directory.mkdir(parents=True, exist_ok=True)
    controller = DemoController()
    _sample(controller.state)
    overlay = Overlay(controller)
    surface = pygame.Surface((PANEL_WIDTH, 1080))

    shots: list[tuple[str, int, dict[str, str] | None, int, Family]] = [
        ('servers', 0, None, 1, Family.XBOX),
        ('channels', 0, {'id': '1000', 'name': 'Retro Night'}, 1, Family.XBOX),
        ('friends', 1, None, 0, Family.PLAYSTATION),
        ('call', 2, None, 2, Family.XBOX),
        ('settings', 3, None, 0, Family.NINTENDO),
    ]
    for name, tab, guild, selected, family in shots:
        controller.current_family = family
        overlay.tab, overlay.tab_x, overlay.sel, overlay.highlight, overlay.scroll = (
            tab,
            float(tab),
            selected,
            float(selected),
            0.0,
        )
        overlay.guild = guild
        overlay.draw(surface)
        pygame.image.save(surface, str(directory / f'{name}.png'))

    controller.setup_link = 'http://192.168.1.20:8099/s/demo-token'
    overlay.qr_url = None
    controller.state.phase = Phase.NO_CONFIG
    overlay.draw(surface)
    pygame.image.save(surface, str(directory / 'setup.png'))

    controller.state.phase = Phase.NO_DISCORD
    controller.state.audio = AudioDevices(output='TV (HDMI)')
    overlay.qr_url = None
    overlay.act(Action.UP)  # status screens ignore navigation
    overlay.draw(surface)
    pygame.image.save(surface, str(directory / 'install.png'))

    controller.state.phase = Phase.INSTALLING
    controller.state.install_progress = 42
    overlay.draw(surface)
    pygame.image.save(surface, str(directory / 'installing.png'))
    print(f'screenshots written to {directory}')
    return 0
