"""The controller driven side panel: Servers / Friends / Call / Settings, plus setup and status screens."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, Protocol, cast

import pygame

from ..controls import Action, Family
from ..i18n import _
from ..session import avatar_key
from ..state import Phase
from ..storage import AppConfig
from . import theme as t
from .qr import qr_surface

if TYPE_CHECKING:
    from pathlib import Path

    from ..state import State

PANEL_WIDTH: Final = 660
ROW: Final = 84
OPEN_ANIMATION: Final = 0.22
TOAST_TIME: Final = 3.0


class Controller(Protocol):
    """What the overlay needs from the daemon."""

    state: State

    def family(self) -> Family: ...
    def image_path(self, key: str, /) -> Path: ...
    def setup_url(self) -> str | None: ...
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
    def recents(self) -> list[dict[str, str]]: ...


@dataclass(slots=True)
class Item:
    kind: str
    label: str = ''
    id: str = ''
    sub: str = ''
    data: Any = None
    active: bool = False


def user_name(user: dict[str, Any], nick: str | None = None, /) -> str:
    return str(nick or user.get('global_name') or user.get('username') or '?')


def fmt_duration(seconds: float, /) -> str:
    s = int(seconds)
    return f'{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}' if s >= 3600 else f'{s // 60}:{s % 60:02d}'


class Overlay:
    TABS: Final = ('Servers', 'Friends', 'Call', 'Settings')

    def __init__(self, controller: Controller, /) -> None:
        self.c = controller
        self.tab = 0
        self.sel = 0
        self.guild: dict[str, str] | None = None
        self.scroll = 0.0
        self.highlight = 0.0
        self.tab_x = 0.0
        self.qr_url: str | None = None
        self.opened_at = 0.0
        self.toasts: list[tuple[float, str]] = []
        self._background: pygame.Surface | None = None
        self._qr_cache: tuple[str, pygame.Surface] | None = None

    # ------------------------------------------------------------------ data
    def on_open(self) -> None:
        with self.c.state.lock:
            in_call = self.c.state.call is not None
        self.tab = 2 if in_call else self.tab
        self.sel, self.highlight, self.scroll, self.tab_x = 0, 0.0, 0.0, float(self.tab)
        self.opened_at = time.monotonic()
        self.qr_url = None

    def toast(self, message: str, /) -> None:
        self.toasts.append((time.monotonic(), message))

    def items(self) -> list[Item]:
        state = self.c.state
        with state.lock:
            if self.tab == 0:
                if self.guild is None:
                    return [Item('guild', str(g['name']), str(g['id'])) for g in state.guilds]
                channels = state.channels.get(self.guild['id'])
                if channels is None:
                    return [Item('info', _('Loading voice channels…'))]
                out: list[Item] = []
                for channel in channels:
                    users = [vs['user'] for vs in channel.get('voice_states', []) if isinstance(vs.get('user'), dict)]
                    active = state.call is not None and state.call.id == channel['id']
                    out.append(Item('channel', str(channel['name']), str(channel['id']), data=users, active=active))
                return out or [Item('info', _('No voice channel on this server'))]
            if self.tab == 1:
                favorites = [Item('dm', f.name, f.channel_id, _('Favorite')) for f in AppConfig.load().favorites]
                known = {item.id for item in favorites}
                recent = [
                    Item('dm', r['name'], r['channel_id'], _('Recent call'))
                    for r in self.c.recents()
                    if r['channel_id'] not in known
                ]
                return favorites + recent or [
                    Item(
                        'empty',
                        _('No friends yet'),
                        sub=_('Add favorites from the setup page. Your private calls show up here automatically.'),
                    )
                ]
            if self.tab == 2:
                if state.call is None:
                    return [Item('empty', _('Not in a call'), sub=_('Join a channel from Servers or call a friend.'))]
                me = (state.user or {}).get('id')
                members = sorted(
                    state.members.items(),
                    key=lambda kv: (kv[0] != me, user_name(kv[1].get('user') or {}, kv[1].get('nick')).lower()),
                )
                return [Item('leave', _('Leave call'))] + [
                    Item('member', '', uid, data=vs, active=uid == me) for uid, vs in members
                ]
            name = user_name(state.user) if state.user else ''
        return [
            Item('setup', _('Open the setup page'), sub=_('Connected as {name}', name=name) if name else ''),
            Item('window', _('Show Discord window')),
            Item('logout', _('Log out')),
        ]

    # --------------------------------------------------------------- actions
    def act(self, action: Action, /) -> None:
        phase = self.c.state.phase
        if self.qr_url is not None or phase is Phase.NO_CONFIG:
            if action is Action.BACK:
                if self.qr_url is not None and phase is not Phase.NO_CONFIG:
                    self.qr_url = None
                else:
                    self.c.close_overlay()
            return
        if phase is not Phase.READY:
            self._act_status(action, phase)
            return
        items = self.items()
        count = len(items)
        if action is Action.UP:
            self.sel = max(0, self.sel - 1)
        elif action is Action.DOWN:
            self.sel = min(count - 1, self.sel + 1)
        elif action in (Action.PREV_TAB, Action.NEXT_TAB):
            self.tab = (self.tab + (1 if action is Action.NEXT_TAB else -1)) % len(self.TABS)
            self.sel, self.guild, self.highlight, self.scroll = 0, None, 0.0, 0.0
        elif action is Action.BACK:
            if self.tab == 0 and self.guild is not None:
                guild_id, self.guild = self.guild['id'], None
                self.sel = next((i for i, item in enumerate(self.items()) if item.id == guild_id), 0)
                self.highlight = self.scroll = float(self.sel)
            else:
                self.c.close_overlay()
        elif action is Action.MUTE:
            if self.c.state.audio.mic is None:
                headset = self.c.state.audio.headset_without_mic
                self.toast(_('Switch your headset to call mode to talk') if headset else _('No microphone connected'))
            self.c.toggle_mute()
        elif action is Action.DEAFEN:
            self.c.toggle_deaf()
        elif (
            action in (Action.LEFT, Action.RIGHT)
            and count
            and items[self.sel].kind == 'member'
            and not items[self.sel].active
        ):
            item = items[self.sel]
            voice_state = cast('dict[str, Any]', item.data)
            volume = max(0, min(200, int(voice_state.get('volume', 100)) + (10 if action is Action.RIGHT else -10)))
            voice_state['volume'] = volume
            self.c.set_user_volume(item.id, volume)
        elif action is Action.CONFIRM and count:
            self._confirm(items[min(self.sel, count - 1)])
        self.sel = max(0, min(self.sel, len(self.items()) - 1))

    def _confirm(self, item: Item, /) -> None:
        if item.kind == 'guild':
            self.guild = {'id': item.id, 'name': item.label}
            self.sel, self.highlight, self.scroll = 0, 0.0, 0.0
            self.c.load_channels(item.id)
        elif item.kind in ('channel', 'dm'):
            self.toast(_('Connecting to {name}…', name=item.label))
            self.c.join(item.id)
            self.tab, self.sel = 2, 0
        elif item.kind == 'leave':
            self.c.leave()
            self.toast(_('Call left'))
        elif item.kind == 'member' and not item.active:
            voice_state = cast('dict[str, Any]', item.data)
            muted = not bool(voice_state.get('mute'))
            voice_state['mute'] = muted
            self.c.set_user_mute(item.id, muted)
        elif item.kind == 'setup':
            self.qr_url = self.c.setup_url()
        elif item.kind == 'window':
            self.c.show_discord_window()
        elif item.kind == 'logout':
            self.c.logout()
            self.toast(_('Logged out'))

    def _act_status(self, action: Action, phase: Phase, /) -> None:
        if action is Action.BACK:
            self.c.close_overlay()
        elif action in (Action.CONFIRM, Action.START):
            if phase is Phase.NO_DISCORD:
                self.c.install_discord()
            elif phase is Phase.LAUNCHING:
                self.c.show_discord_window()
            elif phase in (Phase.ERROR, Phase.INSTALLING):
                self.qr_url = self.c.setup_url()

    # ------------------------------------------------------------- drawing
    def draw(self, surface: pygame.Surface, /) -> None:
        width, height = surface.get_size()
        if self._background is None or self._background.get_size() != (width, height):
            self._background = self._make_background(width, height)
        surface.blit(self._background, (0, 0))
        state = self.c.state
        phase = state.phase
        if self.qr_url is None and phase is Phase.NO_CONFIG:
            self.qr_url = self.c.setup_url()
        if self.qr_url is not None:
            self._draw_setup(surface, width, height, self.qr_url)
            return
        y = self._draw_header(surface, width)
        y = self._draw_status_tiles(surface, width, y + 22)
        if phase is Phase.READY:
            y = self._draw_tabs(surface, width, y + 26)
            self._draw_list(surface, width, y + 20, height - 92)
        else:
            self._draw_phase(surface, width, y + 40, height - 92, phase)
        self._draw_toast(surface, width, height - 92)
        self._draw_footer(surface, width, height)

    @staticmethod
    def _make_background(width: int, height: int, /) -> pygame.Surface:
        background = pygame.Surface((width, height))
        for y in range(height):
            k = (y / height) ** 0.8
            background.fill(
                tuple(int(t.BG_TOP[i] + (t.BG_BOTTOM[i] - t.BG_TOP[i]) * k) for i in range(3)), (0, y, width, 1)
            )
        halo = pygame.Surface((width, height), pygame.SRCALPHA)
        for radius in range(420, 0, -12):
            pygame.draw.circle(halo, (*t.ACCENT, int(26 * (1 - radius / 420) ** 1.6)), (width - 60, 40), radius)
        background.blit(halo, (0, 0))
        edge = pygame.Surface((2, height), pygame.SRCALPHA)
        edge.fill((255, 255, 255, 22))
        background.blit(edge, (0, 0))
        return background

    def _draw_header(self, surface: pygame.Surface, width: int, /) -> int:
        y = 40
        with self.c.state.lock:
            user, call = self.c.state.user, self.c.state.call
        if user is None:
            t.draw_text(surface, 'Discord', (t.PAD, y + 6), 38, t.TEXT, t.BOLD)
            return y + 64
        size = 76
        center = (t.PAD + size // 2, y + size // 2)
        t.circle(surface, t.GREEN if call else t.ACCENT, center, size // 2 + 4)
        t.circle(surface, t.BG_TOP, center, size // 2 + 1)
        surface.blit(t.picture(self.c.image_path(avatar_key(user)), size, user_name(user)), (t.PAD, y))
        t.circle(surface, t.BG_TOP, (t.PAD + size - 8, y + size - 8), 12)
        t.circle(surface, t.GREEN_HI if call else t.GREEN, (t.PAD + size - 8, y + size - 8), 8)
        x = t.PAD + size + 20
        t.draw_text(surface, user_name(user), (x, y + 6), 30, t.TEXT, t.BOLD, max_width=width - x - t.PAD)
        if call is not None:
            rect = t.draw_text(
                surface,
                _('In call · {name}', name=call.name or _('Private call')),
                (x, y + 46),
                19,
                t.GREEN_HI,
                t.BOLD,
                max_width=width - x - t.PAD - 70,
            )
            t.draw_text(surface, fmt_duration(time.time() - call.since), (rect.right + 10, y + 46), 19, t.DIM)
        else:
            t.draw_text(
                surface,
                f'@{user.get("username", "")} · {_("available")}',
                (x, y + 46),
                19,
                t.DIM,
                max_width=width - x - t.PAD,
            )
        return y + size

    def _draw_status_tiles(self, surface: pygame.Surface, width: int, y: int, /) -> int:
        state = self.c.state
        with state.lock:
            audio, mute, deaf = state.audio, state.mute, state.deaf
        family = self.c.family()
        tile_w = (width - t.PAD * 2 - 14) // 2
        if audio.mic is None:
            mic = (
                'none',
                _('No microphone'),
                _('{name} · hi-fi mode', name=audio.headset_without_mic)
                if audio.headset_without_mic
                else _('no microphone connected'),
            )
        elif mute:
            mic = ('off', _('Mic muted'), audio.mic)
        else:
            mic = ('on', _('Mic'), audio.mic)
        sound = ('off', _('Sound off'), audio.output) if deaf else ('on', _('Sound'), audio.output)
        for index, ((status, title, subtitle), icon, action) in enumerate(
            ((mic, t.icon_mic, Action.MUTE), (sound, t.icon_headset, Action.DEAFEN))
        ):
            x = t.PAD + index * (tile_w + 14)
            if status == 'off':
                background, top, color, sub_color = (110, 30, 34, 255), (150, 40, 45), (255, 150, 150), (255, 185, 185)
            elif status == 'none':
                background, top, color, sub_color = (52, 46, 30, 255), (70, 60, 34), t.WARN, (215, 180, 120)
            else:
                background, top, color, sub_color = (*t.CARD, 255), t.CARD_HI, t.TEXT, t.DIM
            surface.blit(t.rounded(tile_w, 64, 18, background, top), (x, y))
            icon(surface, x + 34, y + 32, 26, color, status != 'on')
            if status == 'on':
                t.circle(surface, t.GREEN_HI, (x + 48, y + 46), 5)
            t.draw_text(surface, title, (x + 62, y + 11), 20, color, t.BOLD, max_width=tile_w - 110)
            t.draw_text(surface, subtitle, (x + 62, y + 36), 15, sub_color, max_width=tile_w - 110)
            t.button(surface, x + tile_w - 26, y + 32, action, family, 13)
        return y + 64

    def _draw_tabs(self, surface: pygame.Surface, width: int, y: int, /) -> int:
        left, right = t.BUMPERS[self.c.family()]
        t.bumper(surface, t.PAD, y + 9, left)
        t.bumper(surface, width - t.PAD - 46, y + 9, right)
        x0, x1 = t.PAD + 58, width - t.PAD - 58
        segment = (x1 - x0) / len(self.TABS)
        surface.blit(t.rounded(int(x1 - x0), 44, 22, (255, 255, 255, 14)), (x0, y))
        self.tab_x += (self.tab - self.tab_x) * 0.35
        hx = x0 + 4 + self.tab_x * segment
        surface.blit(t.glow(int(segment - 8), 36, 18, t.ACCENT, 10), (hx - 10, y - 6))
        surface.blit(t.rounded(int(segment - 8), 36, 18, (*t.ACCENT, 255), t.ACCENT_HI), (hx, y + 4))
        for index, name in enumerate(self.TABS):
            color = t.TEXT if index == self.tab else t.DIM
            t.draw_text(
                surface, _(name), (x0 + segment * index + segment / 2, y + 22), 18, color, t.BOLD, anchor='center'
            )
        return y + 44

    def _draw_empty(
        self, surface: pygame.Surface, width: int, top: int, bottom: int, title: str, subtitle: str, /
    ) -> None:
        cy = top + (bottom - top) // 3
        t.circle(surface, (255, 255, 255, 16), (width // 2, cy), 54)
        t.icon_headset(surface, width // 2, cy, 46, t.DIM)
        t.draw_text(surface, title, (width // 2, cy + 86), 27, t.TEXT, t.BOLD, anchor='center')
        for row, line in enumerate(t.wrap(subtitle, 19, width - t.PAD * 4)):
            t.draw_text(surface, line, (width // 2, cy + 126 + row * 28), 19, t.DIM, anchor='center')

    def _draw_phase(self, surface: pygame.Surface, width: int, top: int, bottom: int, phase: Phase, /) -> None:
        family = self.c.family()
        confirm = t.button_label(Action.CONFIRM, family)
        state = self.c.state
        texts = {
            Phase.NO_DISCORD: (
                _('Discord is not installed'),
                _('Press {button} to install it from Flathub (about 250 MB).', button=confirm),
            ),
            Phase.INSTALLING: (
                _('Installing Discord… {percent}%', percent=state.install_progress),
                _('Meanwhile, press {button} to set it up from your phone.', button=confirm),
            ),
            Phase.LAUNCHING: (_('Starting Discord…'), _('Log in to Discord once in its window, then come back here.')),
            Phase.CONNECTING: (_('Connecting…'), ''),
            Phase.AUTHORIZE: (
                _('Authorization'),
                _(
                    'Accept the request in the Discord window: move the pointer with the stick, {button} clicks.',
                    button=confirm,
                ),
            ),
            Phase.ERROR: (_('Connection failed'), state.error),
            Phase.STARTING: (_('Starting…'), ''),
        }
        title, subtitle = texts.get(phase, ('', ''))
        self._draw_empty(surface, width, top, bottom, title, subtitle)
        if phase is Phase.INSTALLING:
            bar_w, y = width - t.PAD * 4, top + (bottom - top) // 3 + 180
            surface.blit(t.rounded(bar_w, 10, 5, (255, 255, 255, 40)), (t.PAD * 2, y))
            fill = max(10, int(bar_w * state.install_progress / 100))
            surface.blit(t.rounded(fill, 10, 5, (*t.ACCENT_HI, 255)), (t.PAD * 2, y))
        elif phase in (Phase.LAUNCHING, Phase.ERROR):
            label = _('Show Discord window') if phase is Phase.LAUNCHING else _('Open the setup page')
            y = top + (bottom - top) // 3 + 200
            surface.blit(t.rounded(width - t.PAD * 4, 56, 28, (*t.ACCENT, 255), t.ACCENT_HI), (t.PAD * 2, y))
            t.button(surface, t.PAD * 2 + 34, y + 28, Action.CONFIRM, family, 14)
            t.draw_text(surface, label, (t.PAD * 2 + 60, y + 28), 20, t.WHITE, t.BOLD, anchor='midleft')

    def _draw_setup(self, surface: pygame.Surface, width: int, height: int, url: str, /) -> None:
        t.draw_text(surface, _('Set up Discord'), (t.PAD, 48), 36, t.TEXT, t.BOLD)
        t.draw_text(surface, _('Scan this code with your phone'), (t.PAD, 100), 21, t.DIM)
        size = width - t.PAD * 2 - 120
        if self._qr_cache is None or self._qr_cache[0] != url:
            self._qr_cache = (url, qr_surface(url, size))
        code = self._qr_cache[1]
        card = t.rounded(code.get_width() + 40, code.get_height() + 40, 28, (255, 255, 255, 255))
        x = (width - card.get_width()) // 2
        surface.blit(t.glow(card.get_width(), card.get_height(), 28, t.ACCENT, 22), (x - 22, 160 - 22))
        surface.blit(card, (x, 160))
        surface.blit(code, (x + 20, 180))
        y = 160 + card.get_height() + 30
        t.draw_text(
            surface, url, (width // 2, y), 18, t.ACCENT_HI, t.BOLD, anchor='center', max_width=width - t.PAD * 2
        )
        y += 46
        for line in (
            _('Your phone must be on the same network as this console.'),
            _('The page explains how to create your free Discord application (2 minutes).'),
        ):
            for row in t.wrap(line, 19, width - t.PAD * 3):
                t.draw_text(surface, row, (width // 2, y), 19, t.DIM, anchor='center')
                y += 28
            y += 8
        dots = '.' * (1 + int(time.monotonic() * 2) % 3)
        t.draw_text(
            surface,
            _('Waiting for your phone…').rstrip('…') + dots,
            (width // 2, y + 20),
            19,
            t.TEXT,
            t.BOLD,
            anchor='center',
        )
        self._draw_footer(surface, width, height, setup=True)

    def _draw_list(self, surface: pygame.Surface, width: int, top: int, bottom: int, /) -> None:
        family = self.c.family()
        if self.tab == 0 and self.guild is not None:
            surface.blit(
                t.picture(self.c.image_path(f'g{self.guild["id"]}'), 30, self.guild['name'], squircle=True),
                (t.PAD, top),
            )
            t.draw_text(
                surface,
                self.guild['name'],
                (t.PAD + 42, top + 15),
                20,
                t.TEXT,
                t.BOLD,
                max_width=width - t.PAD * 2 - 160,
                anchor='midleft',
            )
            back = f'{t.button_label(Action.BACK, family)}  {_("back")}'
            t.draw_text(surface, back, (width - t.PAD, top + 15), 16, t.DIM, anchor='midright')
            top += 48
        items = self.items()
        if len(items) == 1 and items[0].kind == 'empty':
            self._draw_empty(surface, width, top, bottom, items[0].label, items[0].sub)
            return
        self.sel = max(0, min(self.sel, len(items) - 1))
        visible = max(1, (bottom - top) // ROW)
        target = min(max(0, self.sel - visible // 2), max(0, len(items) - visible))
        self.scroll += (target - self.scroll) * 0.3
        self.highlight += (self.sel - self.highlight) * 0.35
        clip = surface.get_clip()
        surface.set_clip(pygame.Rect(0, top - 14, width, bottom - top + 14))
        card_w, card_h = width - t.PAD * 2, ROW - 10
        for index in range(len(items)):
            y = top + (index - self.scroll) * ROW
            if top - ROW < y < bottom and index != self.sel:
                surface.blit(t.rounded(card_w, card_h, 18, (*t.CARD, 235), t.CARD_HI), (t.PAD, int(y)))
        hy = int(top + (self.highlight - self.scroll) * ROW)
        surface.blit(t.glow(card_w, card_h, 18, t.ACCENT, 16), (t.PAD - 16, hy - 16))
        surface.blit(t.rounded(card_w, card_h, 18, (*t.ACCENT, 255), t.ACCENT_HI), (t.PAD, hy))
        for index, item in enumerate(items):
            y = top + (index - self.scroll) * ROW
            if top - ROW < y < bottom:
                self._draw_item(surface, item, t.PAD, int(y), card_w, card_h, index == self.sel, family)
        surface.set_clip(clip)
        if len(items) > visible:
            track = bottom - top
            thumb = max(40, int(track * visible / len(items)))
            ty = top + (track - thumb) * (self.scroll / max(1, len(items) - visible))
            surface.blit(t.rounded(4, thumb, 2, (255, 255, 255, 60)), (width - 12, int(ty)))

    def _draw_item(
        self, surface: pygame.Surface, item: Item, x: int, y: int, w: int, h: int, selected: bool, family: Family, /
    ) -> None:
        cy = y + h // 2
        dim = (225, 228, 255) if selected else t.DIM
        kind = item.kind
        if kind == 'info':
            t.draw_text(surface, item.label, (x + 24, cy), 20, t.DIM, anchor='midleft', max_width=w - 48)
        elif kind == 'guild':
            surface.blit(t.picture(self.c.image_path(f'g{item.id}'), 50, item.label, squircle=True), (x + 14, cy - 25))
            t.draw_text(surface, item.label, (x + 80, cy), 22, t.TEXT, t.BOLD, anchor='midleft', max_width=w - 130)
            t.icon_chevron(surface, x + w - 26, cy, 16, t.TEXT if selected else t.FAINT)
        elif kind == 'channel':
            users = cast('list[dict[str, Any]]', item.data)
            surface.blit(t.rounded(46, 46, 14, (255, 255, 255, 40 if selected else 14)), (x + 16, cy - 23))
            t.icon_speaker(surface, x + 39, cy, 22, t.GREEN_HI if item.active else t.TEXT if selected else t.DIM)
            has_sub = bool(users) or item.active
            t.draw_text(
                surface,
                item.label,
                (x + 78, cy - (11 if has_sub else 0)),
                21,
                t.TEXT,
                t.BOLD,
                anchor='midleft',
                max_width=w - 260,
            )
            if has_sub:
                sub = (_('You are here · ') if item.active else '') + _('{count} connected', count=len(users))
                t.draw_text(
                    surface,
                    sub,
                    (x + 78, cy + 15),
                    15,
                    t.GREEN_HI if item.active else dim,
                    anchor='midleft',
                    max_width=w - 260,
                )
            ax = x + w - 22
            for user in list(reversed(users[:4])):
                ax -= 28
                t.circle(surface, t.ACCENT if selected else t.CARD, (ax + 17, cy), 19)
                surface.blit(t.picture(self.c.image_path(avatar_key(user)), 34, user_name(user)), (ax, cy - 17))
            if len(users) > 4:
                t.draw_text(surface, f'+{len(users) - 4}', (ax - 8, cy), 16, dim, t.BOLD, anchor='midright')
        elif kind == 'dm':
            surface.blit(t.picture(self.c.image_path(f'dm{item.id}'), 52, item.label), (x + 14, cy - 26))
            t.draw_text(surface, item.label, (x + 82, cy - 11), 22, t.TEXT, t.BOLD, anchor='midleft', max_width=w - 250)
            t.draw_text(surface, item.sub, (x + 82, cy + 15), 15, dim, anchor='midleft')
            button_w = 128
            surface.blit(
                t.rounded(button_w, 40, 20, (255, 255, 255, 255) if selected else (*t.GREEN, 255)),
                (x + w - button_w - 14, cy - 20),
            )
            color = t.ACCENT if selected else t.WHITE
            t.icon_phone(surface, x + w - button_w + 12, cy, 16, color)
            t.draw_text(surface, _('Dial'), (x + w - button_w + 30, cy), 18, color, t.BOLD, anchor='midleft')
        elif kind == 'leave':
            surface.blit(t.rounded(46, 46, 23, (*t.RED, 255)), (x + 16, cy - 23))
            t.icon_cross(surface, x + 39, cy, 16, t.WHITE)
            t.draw_text(surface, item.label, (x + 78, cy), 22, t.TEXT, t.BOLD, anchor='midleft')
        elif kind == 'member':
            self._draw_member(surface, item, x, cy, w, selected, family)
        else:  # settings entries
            surface.blit(t.rounded(46, 46, 14, (255, 255, 255, 40 if selected else 14)), (x + 16, cy - 23))
            icon_color = t.RED if kind == 'logout' and not selected else t.TEXT
            if kind == 'setup':
                t.icon_gear(surface, x + 39, cy, 22, icon_color)
            elif kind == 'window':
                pygame.draw.rect(surface, icon_color, (x + 28, cy - 9, 22, 18), 3, border_radius=3)
            else:
                t.icon_cross(surface, x + 39, cy, 14, icon_color)
            t.draw_text(
                surface,
                item.label,
                (x + 78, cy - (11 if item.sub else 0)),
                21,
                t.TEXT,
                t.BOLD,
                anchor='midleft',
                max_width=w - 110,
            )
            if item.sub:
                t.draw_text(surface, item.sub, (x + 78, cy + 15), 15, dim, anchor='midleft', max_width=w - 110)

    def _draw_member(
        self, surface: pygame.Surface, item: Item, x: int, cy: int, w: int, selected: bool, family: Family, /
    ) -> None:
        voice_state = cast('dict[str, Any]', item.data)
        user = cast('dict[str, Any]', voice_state.get('user') or {})
        with self.c.state.lock:
            talking = item.id in self.c.state.speaking
        cx = x + 42
        if talking:
            t.circle(surface, t.GREEN_HI, (cx, cy), int(29 + 3 + 2 * math.sin(time.monotonic() * 9)), 3)
        surface.blit(t.picture(self.c.image_path(avatar_key(user)), 54, user_name(user)), (cx - 27, cy - 27))
        flags = cast('dict[str, Any]', voice_state.get('voice_state') or {})
        self_mute = bool(flags.get('self_mute') or flags.get('mute'))
        self_deaf = bool(flags.get('self_deaf') or flags.get('deaf'))
        if self_mute or self_deaf:
            t.circle(surface, t.BG_BOTTOM, (cx + 20, cy + 20), 12)
            (t.icon_headset if self_deaf else t.icon_mic)(surface, cx + 20, cy + 20, 14, t.RED, True)
        name = user_name(user, voice_state.get('nick'))
        t.draw_text(
            surface,
            f'{name}  · {_("you")}' if item.active else name,
            (x + 84, cy - 12),
            21,
            t.TEXT,
            t.BOLD,
            anchor='midleft',
            max_width=w - 300,
        )
        if voice_state.get('mute') and not item.active:
            status, color = _('muted for you'), t.RED
        elif talking:
            status, color = _('speaking…'), t.GREEN_HI
        elif self_deaf:
            status, color = _('sound off'), (255, 140, 140)
        elif self_mute:
            status, color = _('mic off'), (255, 140, 140)
        else:
            status, color = _('connected'), (225, 228, 255) if selected else t.DIM
        t.draw_text(surface, status, (x + 84, cy + 14), 15, color, anchor='midleft')
        if item.active:
            return
        volume = int(voice_state.get('volume', 100))
        bx, bw = x + w - 196, 130
        surface.blit(t.rounded(bw, 8, 4, (255, 255, 255, 50)), (bx, cy - 4))
        fill = max(8, int(bw * min(volume, 200) / 200))
        surface.blit(t.rounded(fill, 8, 4, (255, 255, 255, 255) if selected else (*t.ACCENT_HI, 255)), (bx, cy - 4))
        t.circle(surface, t.WHITE, (bx + fill, cy), 9 if selected else 7)
        t.draw_text(surface, f'{volume}%', (x + w - 18, cy), 16, t.TEXT, t.BOLD, anchor='midright')
        if selected:
            hint = f'◀ ▶ {_("volume")}   {t.button_label(Action.CONFIRM, family)} {_("mute")}'
            t.draw_text(surface, hint, (bx, cy + 22), 13, (225, 228, 255))

    def _draw_toast(self, surface: pygame.Surface, width: int, bottom: int, /) -> None:
        now = time.monotonic()
        self.toasts = [toast for toast in self.toasts if now - toast[0] < TOAST_TIME]
        if not self.toasts:
            return
        started, message = self.toasts[-1]
        fade = min(1.0, (now - started) * 6, (TOAST_TIME - (now - started)) * 4)
        image = t.render(message, 19, t.TEXT, t.BOLD)
        box_w = min(width - 60, image.get_width() + 48)
        y = bottom - 66 + int((1 - fade) * 20)
        surface.blit(t.rounded(box_w, 48, 24, (20, 22, 28, 245)), ((width - box_w) // 2, y))
        surface.blit(image, image.get_rect(center=(width // 2, y + 24)))

    def _draw_footer(self, surface: pygame.Surface, width: int, height: int, /, *, setup: bool = False) -> None:
        family = self.c.family()
        surface.blit(t.rounded(width - t.PAD * 2 + 16, 56, 28, (255, 255, 255, 12)), (t.PAD - 8, height - 76))
        x, cy = t.PAD + 10, height - 48
        hints = (
            ((Action.BACK, _('Back')),)
            if setup
            else (
                (Action.CONFIRM, _('Select')),
                (Action.BACK, _('Back')),
                (Action.MUTE, _('Mic')),
                (Action.DEAFEN, _('Sound')),
            )
        )
        for action, label in hints:
            t.button(surface, x + 13, cy, action, family, 13)
            x = t.draw_text(surface, label, (x + 32, cy), 17, t.DIM, t.BOLD, anchor='midleft').right + 22
        t.guide_button(surface, width - t.PAD - 14, cy, family)
        t.draw_text(surface, _('Close'), (width - t.PAD - 34, cy), 17, t.DIM, t.BOLD, anchor='midright')

    def present(self, screen: pygame.Surface, canvas: pygame.Surface, /) -> None:
        """Opening animation: the content slides in from the right while fading in."""
        progress = min(1.0, (time.monotonic() - self.opened_at) / OPEN_ANIMATION)
        eased = 1 - (1 - progress) ** 3
        if eased >= 1:
            screen.blit(canvas, (0, 0))
        else:
            screen.fill(t.BG_BOTTOM)
            canvas.set_alpha(int(255 * eased))
            screen.blit(canvas, (int((1 - eased) * 70), 0))
            canvas.set_alpha(None)
