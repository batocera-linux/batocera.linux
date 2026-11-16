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

from typing import TYPE_CHECKING

from batocera_common.paths import CONFIGS, SAVES, SCREENSHOTS
from batocera_launch.emulators.keisho import _merge_ini, migrate_batocera_conf_text, migrate_files

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem


def _write(path: Path, text: str = '', /) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_conf_renames_the_emulators_and_the_sm2_options() -> None:
    conf = (
        '# model2.emulator=sm2-emu\n'
        'model2.emulator=sm2-emu\n'
        'model2.core=sm2-emu\n'
        'model2["daytona.zip"].sm2_vsync=1\n'
        'model2.sm2_render_scale=4\n'
        'model2.core=sm2emu\n'
        'model3.emulator=supermodel\n'
        'model3.core=supermodel\n'
    )

    assert migrate_batocera_conf_text(conf) == (
        '# model2.emulator=sm2-emu\n'
        'model2.emulator=keisho\n'
        'model2.core=keisho\n'
        'model2["daytona.zip"].keisho_vsync=1\n'
        'model2.keisho_render_scale=4\n'
        'model2.core=sm2emu\n'
        'model3.emulator=keisho\n'
        'model3.core=keisho\n'
    )


def test_conf_carries_supermodel_options_over_and_drops_the_rest() -> None:
    conf = (
        'model3.graphics_backend=Vulkan\n'
        'model3.m3_wideScreen=1\n'
        'model3.m3_stretch=1\n'
        'model3["scud.zip"].m3_vsync=0\n'
        'model3.m3_renderscale=0\n'
        'model3.crosshairs=3\n'
        'model3.forceFeedback=1\n'
        'model3.m3_audio_channels=4\n'
        'model3.m3_outputs=net\n'
        'model3.m3_outputs_tcp=8001\n'
        'model3.engine3D=new3d\n'
        'model3.ppcFreq=50\n'
        'model3.use_wheels=1\n'
        'n64.graphics_backend=Vulkan\n'
    )

    assert migrate_batocera_conf_text(conf) == (
        'model3.keisho_graphics_backend=vulkan\n'
        'model3.keisho_aspect_mode=16:9\n'
        'model3["scud.zip"].keisho_vsync=0\n'
        'model3.keisho_lightgun_crosshair=1\n'
        'model3.keisho_wheel_ffb=1\n'
        'model3.keisho_surround=1\n'
        'model3.keisho_outputs_network=1\n'
        'model3.keisho_outputs_network_port=8001\n'
        'model3.use_wheels=1\n'
        'n64.graphics_backend=Vulkan\n'
    )


def test_conf_keeps_a_keisho_option_already_set() -> None:
    conf = 'model2.sm2_vsync=1\nmodel2.keisho_vsync=0\n'

    assert migrate_batocera_conf_text(conf) == 'model2.keisho_vsync=0\n'


def test_conf_without_old_settings_is_unchanged() -> None:
    conf = 'global.videomode=default\n\n# a comment\nmodel2.emulator=keisho\n'

    assert migrate_batocera_conf_text(conf) == conf


def test_merge_ini_replaces_managed_keys_and_adds_new_ones_before_sections() -> None:
    existing = (
        '# Keisho settings\nvsync = true\n# fullscreen = false\nlog_level = debug\n[daytona]\npad1_button_button1 = 3\n'
    )

    assert _merge_ini(existing, {'vsync': 'false', 'fullscreen': 'true'}) == (
        '# Keisho settings\nvsync = false\n# fullscreen = false\nlog_level = debug\nfullscreen = true\n'
        '[daytona]\npad1_button_button1 = 3\n'
    )


def test_migrate_files_moves_sm2_emu_and_supermodel_data(fake_fs: FakeFilesystem) -> None:
    _write(CONFIGS / 'sm2-emu' / 'sm2-emu.ini', 'rom_dir = /userdata/roms/model2\n')
    _write(CONFIGS / 'sm2-emu' / 'crosshairs' / 'default.png')
    _write(SAVES / 'model2' / 'sm2-emu' / 'daytona.nv', 'old')
    _write(SAVES / 'model2' / 'sm2-emu' / 'states' / 'daytona.quick.sm2state')
    _write(SAVES / 'model1' / 'sm2-emu' / 'vr.nv')
    _write(SCREENSHOTS / 'sm2-emu' / 'daytona-1.png')
    _write(SAVES / 'supermodel' / 'NVRAM' / 'scud.nv')
    _write(SAVES / 'supermodel' / 'NVRAM' / 'lostwsga (Calibrated for 4x3 resolutions).nv')
    _write(SAVES / 'supermodel' / 'Saves' / 'scud.st0')
    _write(SCREENSHOTS / 'supermodel' / 'scud.bmp')

    migrate_files()

    assert (CONFIGS / 'keisho' / 'keisho.ini').read_text() == 'rom_dir = /userdata/roms/model2\n'
    assert (CONFIGS / 'keisho' / 'crosshairs' / 'default.png').exists()
    assert (SAVES / 'model2' / 'keisho' / 'daytona.nv').read_text() == 'old'
    assert (SAVES / 'model2' / 'keisho' / 'states' / 'daytona.quick.sm2state').exists()
    assert (SAVES / 'model1' / 'keisho' / 'vr.nv').exists()
    assert (SAVES / 'model3' / 'keisho' / 'scud.nv').exists()
    assert (SAVES / 'model3' / 'keisho' / 'lostwsga (Calibrated for 4x3 resolutions).nv').exists()
    assert (SCREENSHOTS / 'keisho' / 'daytona-1.png').exists()
    assert (SCREENSHOTS / 'keisho' / 'scud.bmp').exists()

    assert not (CONFIGS / 'sm2-emu').exists()
    assert not (SAVES / 'model2' / 'sm2-emu').exists()
    assert not (SAVES / 'model1' / 'sm2-emu').exists()
    assert not (SCREENSHOTS / 'sm2-emu').exists()
    assert not (SCREENSHOTS / 'supermodel').exists()
    assert not (SAVES / 'supermodel' / 'NVRAM').exists()
    # supermodel's save states can't be loaded
    assert (SAVES / 'supermodel' / 'Saves' / 'scud.st0').exists()


def test_migrate_files_never_overwrites_keisho_files(fake_fs: FakeFilesystem) -> None:
    _write(CONFIGS / 'sm2-emu' / 'sm2-emu.ini', 'old\n')
    _write(CONFIGS / 'keisho' / 'keisho.ini', 'new\n')
    _write(SAVES / 'model2' / 'sm2-emu' / 'daytona.nv', 'old')
    _write(SAVES / 'model2' / 'keisho' / 'daytona.nv', 'new')

    migrate_files()

    assert (CONFIGS / 'keisho' / 'keisho.ini').read_text() == 'new\n'
    assert (SAVES / 'model2' / 'keisho' / 'daytona.nv').read_text() == 'new'
    assert (CONFIGS / 'sm2-emu' / 'sm2-emu.ini').read_text() == 'old\n'
    assert (SAVES / 'model2' / 'sm2-emu' / 'daytona.nv').read_text() == 'old'
    assert not (CONFIGS / 'keisho' / 'sm2-emu.ini').exists()


def test_migrate_files_without_old_data_does_nothing(fake_fs: FakeFilesystem) -> None:
    migrate_files()

    assert not (CONFIGS / 'keisho').exists()
    assert not (SAVES / 'model3' / 'keisho').exists()
