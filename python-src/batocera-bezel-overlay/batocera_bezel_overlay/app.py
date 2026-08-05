from __future__ import annotations

import logging
import sys
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

import gi
from gi.repository import GLib

try:
    gi.require_version('Gio', '2.0')
    gi.require_version('Gtk', '3.0')

    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)

if TYPE_CHECKING:
    from batocera_bezel_overlay.overlay import Overlay


def _get_log_level(level_str: str) -> int:
    match level_str.lower():
        case 'debug':
            return logging.DEBUG
        case 'info':
            return logging.INFO
        case 'warning':
            return logging.WARNING
        case _:
            return logging.ERROR


class Application(Gtk.Application):
    __gtype_name__ = 'BezelOverlayApplication'

    session_type: str
    overlay: Overlay | None

    image_path: str
    dimensions: tuple[int, int]

    def __init__(self, session_type: str) -> None:
        super().__init__(
            application_id='org.batocera.bezel-overlay',
            flags=('handles-command-line', 'non-unique'),
            version=version('batocera-bezel-overlay'),
        )

        self.set_option_context_parameter_string('IMAGE_PATH WIDTH HEIGHT')

        self.add_main_option('log-level', 0, GLib.OptionFlags.NONE, GLib.OptionArg.STRING, 'Log level', 'LEVEL')
        self.add_main_option('log-file', 0, GLib.OptionFlags.NONE, GLib.OptionArg.FILENAME, 'Log file path', 'FILE')
        self.add_main_option('version', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE, 'Show version')

        self.session_type = session_type
        self.overlay = None

    def do_handle_local_options(self, options: GLib.VariantDict, /) -> int:
        Gtk.Application.do_handle_local_options(self, options)

        if options.contains('version'):
            print(self.get_version())
            return 0

        log_level_value = options.lookup_value('log-level', GLib.VariantType.new('s'))
        log_level = (
            _get_log_level(log_level_value.get_string().lower()) if log_level_value is not None else logging.INFO
        )

        log_file_value = options.lookup_value('log-file', GLib.VariantType.new('s'))
        log_file = Path(log_file_value.get_string()).expanduser() if log_file_value is not None else None

        handlers: list[logging.Handler] = [logging.StreamHandler()]

        if log_file is not None:
            handlers.append(logging.FileHandler(log_file, encoding='utf-8'))

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s %(levelname)s (%(filename)s:%(lineno)d):%(funcName)s %(message)s',
            handlers=handlers,
        )

        return -1

    def do_command_line(self, command_line: Gio.ApplicationCommandLine) -> int:
        Gtk.Application.do_command_line(self, command_line)

        args = command_line.get_arguments()[1:]

        if len(args) != 3:
            command_line.printerr_literal('Usage: batocera-bezel-overlay IMAGE_PATH WIDTH HEIGHT\n')
            return 2

        image_path_file = command_line.create_file_for_arg(args[0])
        image_path = image_path_file.get_path()

        if image_path is None:
            command_line.printerr_literal(f'Error: Invalid image path: {args[0]}\n')
            return 3

        self.image_path = image_path

        try:
            self.dimensions = (int(args[1]), int(args[2]))
        except ValueError:
            command_line.printerr_literal('Width and height must be integers.\n')
            return 4

        self.activate()

        return 0

    def do_activate(self) -> None:
        if 'wayland' in self.session_type:
            from batocera_bezel_overlay.overlay import WaylandOverlay as Overlay
        else:
            from batocera_bezel_overlay.overlay import X11Overlay as Overlay

        overlay = Overlay(self.image_path, self.dimensions)
        self.add_window(overlay)

        overlay.present()
