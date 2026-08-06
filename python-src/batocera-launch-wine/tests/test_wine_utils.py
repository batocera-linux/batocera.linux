from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch import BatoceraException
from batocera_launch_wine import wine

if TYPE_CHECKING:
    from collections.abc import Callable


def _prime_path(marker: Path, /) -> Callable[[str], Path]:
    def path(name: str) -> Path:
        return marker if name == '/var/tmp/nvidia.prime' else Path(name)

    return path


def _autorun(rom: Path, content: str) -> Path:
    rom.mkdir(parents=True, exist_ok=True)
    (rom / 'autorun.cmd').write_text(content)
    return rom


def _exe(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('MZ')
    return path


class TestGetAutorunVars:
    def test_missing_file_gives_nothing(self, tmp_path: Path) -> None:
        assert wine.get_autorun_vars(tmp_path) == {}

    def test_keys_are_upper_cased_and_values_unquoted(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'dir=drive_c/Game\ncmd="game.exe"\n')

        assert wine.get_autorun_vars(rom) == {'DIR': 'drive_c/Game', 'CMD': 'game.exe'}

    def test_crlf_and_bom_are_tolerated(self, tmp_path: Path) -> None:
        rom = tmp_path / 'game'
        rom.mkdir()
        (rom / 'autorun.cmd').write_bytes('\ufeffDIR=drive_c/Game\r\nCMD="game.exe"\r\n'.encode())

        assert wine.get_autorun_vars(rom) == {'DIR': 'drive_c/Game', 'CMD': 'game.exe'}

    def test_the_first_value_of_a_key_wins(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'CMD=first.exe\nCMD=second.exe\n')

        assert wine.get_autorun_vars(rom)['CMD'] == 'first.exe'

    def test_blank_lines_and_valueless_keys_are_skipped(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', '\nCMD=game.exe\nDIR=\nnonsense\n')

        assert wine.get_autorun_vars(rom) == {'CMD': 'game.exe'}


class TestGetGameCommand:
    def test_without_an_autorun_it_raises(self, tmp_path: Path) -> None:
        with pytest.raises(BatoceraException):
            wine.get_game_command(tmp_path)

    def test_an_autorun_naming_no_cmd_raises(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'DIR=drive_c/Game\n')

        with pytest.raises(BatoceraException):
            wine.get_game_command(rom)

    def test_a_cmd_that_does_not_exist_raises(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'CMD=nothere.exe\n')

        with pytest.raises(BatoceraException):
            wine.get_game_command(rom)

    def test_the_exe_is_resolved_under_the_dir(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'DIR=drive_c/Program Files/Game\nCMD="game.exe"\n')
        exe = _exe(rom / 'drive_c' / 'Program Files' / 'Game' / 'game.exe')

        assert wine.get_game_command(rom) == (exe, [])

    def test_arguments_after_the_exe_are_kept(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'CMD=game.exe -windowed /fast\n')
        exe = _exe(rom / 'game.exe')

        assert wine.get_game_command(rom) == (exe, ['-windowed', '/fast'])

    def test_an_unquoted_name_with_spaces_is_taken_whole(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'CMD=my game.exe\n')
        exe = _exe(rom / 'my game.exe')

        assert wine.get_game_command(rom) == (exe, [])

    def test_a_windows_path_in_cmd_is_resolved(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', r'CMD=bin\game.exe' + '\n')
        exe = _exe(rom / 'bin' / 'game.exe')

        assert wine.get_game_command(rom) == (exe, [])

    def test_a_dir_that_does_not_exist_falls_back_to_the_rom(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'DIR=drive_c/Nowhere\nCMD=game.exe\n')
        exe = _exe(rom / 'game.exe')

        assert wine.get_game_dir(rom) == rom
        assert wine.get_game_command(rom) == (exe, [])


class TestGetAutorunEnvironment:
    def test_nothing_asked_gives_nothing(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'CMD=game.exe\n')

        assert wine.get_autorun_environment(rom) == {}

    def test_lang_becomes_lc_all(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'CMD=game.exe\nLANG=ja_JP.UTF-8\n')

        assert wine.get_autorun_environment(rom) == {'LC_ALL': 'ja_JP.UTF-8'}

    def test_env_is_split_into_assignments(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'game', 'CMD=game.exe\nENV=SDL_AUDIODRIVER=alsa MESA_GL_VERSION_OVERRIDE=3.3\n')

        assert wine.get_autorun_environment(rom) == {
            'SDL_AUDIODRIVER': 'alsa',
            'MESA_GL_VERSION_OVERRIDE': '3.3',
        }


class TestFindGameExecutables:
    def test_the_game_is_found_under_program_files(self, tmp_path: Path) -> None:
        _exe(tmp_path / 'drive_c' / 'Program Files' / 'Game' / 'game.exe')

        assert wine.find_game_executables(tmp_path) == [Path('drive_c/Program Files/Game/game.exe')]

    @pytest.mark.parametrize(
        'name',
        [
            'drive_c/Program Files/Game/unins000.exe',
            'drive_c/Program Files/Game/setup.exe',
            'drive_c/Program Files/Game/install.exe',
            'drive_c/Program Files/Game/unwise32.exe',
            'drive_c/Program Files/Internet Explorer/iexplore.exe',
            'drive_c/Program Files/Windows Media Player/wmplayer.exe',
            'drive_c/Program Files/Windows NT/Accessories/wordpad.exe',
        ],
    )
    def test_what_is_not_the_game_is_filtered_out(self, tmp_path: Path, name: str) -> None:
        _exe(tmp_path / name)

        assert wine.find_game_executables(tmp_path) == []

    def test_the_windows_directory_is_outside_the_default_mask(self, tmp_path: Path) -> None:
        _exe(tmp_path / 'drive_c' / 'windows' / 'system32' / 'notepad.exe')

        assert wine.find_game_executables(tmp_path) == []

    def test_a_dot_mask_searches_everything_but_still_filters(self, tmp_path: Path) -> None:
        _exe(tmp_path / 'bin' / 'game.exe')
        _exe(tmp_path / 'drive_c' / 'windows' / 'system32' / 'notepad.exe')

        assert wine.find_game_executables(tmp_path, '.') == [Path('bin/game.exe')]

    def test_several_candidates_come_back_sorted(self, tmp_path: Path) -> None:
        for name in ('c.exe', 'a.exe', 'b.exe'):
            _exe(tmp_path / 'drive_c' / 'Program Files' / 'Game' / name)

        assert [p.name for p in wine.find_game_executables(tmp_path)] == ['a.exe', 'b.exe', 'c.exe']

    def test_non_executables_are_ignored(self, tmp_path: Path) -> None:
        _exe(tmp_path / 'drive_c' / 'Program Files' / 'Game' / 'readme.txt')

        assert wine.find_game_executables(tmp_path) == []

    def test_a_user_regex_file_filters_further(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _exe(tmp_path / 'drive_c' / 'Program Files' / 'Game' / 'game.exe')
        _exe(tmp_path / 'drive_c' / 'Program Files' / 'Game' / 'launcher.exe')

        regexes = tmp_path / 'autorun-regex.txt'
        regexes.write_text('# drop the launcher\n\n/launcher\\.exe$\n')
        monkeypatch.setattr(wine, '_AUTORUN_REGEX_FILES', (regexes,))

        assert [p.name for p in wine.find_game_executables(tmp_path)] == ['game.exe']

    def test_a_broken_user_regex_is_ignored(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _exe(tmp_path / 'drive_c' / 'Program Files' / 'Game' / 'game.exe')

        regexes = tmp_path / 'autorun-regex.txt'
        regexes.write_text('*[unclosed\n')
        monkeypatch.setattr(wine, '_AUTORUN_REGEX_FILES', (regexes,))

        assert [p.name for p in wine.find_game_executables(tmp_path)] == ['game.exe']


class TestWriteAutorunCmd:
    def test_an_executable_is_named(self, tmp_path: Path) -> None:
        wine.write_autorun_cmd(tmp_path, Path('drive_c/Program Files/Game/game.exe'))

        assert (tmp_path / 'autorun.cmd').read_text() == 'DIR=drive_c/Program Files/Game\nCMD="game.exe"\n'

    def test_without_one_a_template_is_left(self, tmp_path: Path) -> None:
        wine.write_autorun_cmd(tmp_path, None)

        assert (tmp_path / 'autorun.cmd').read_text().startswith('#DIR=')

    def test_what_is_written_can_be_read_back(self, tmp_path: Path) -> None:
        exe = _exe(tmp_path / 'drive_c' / 'Program Files' / 'Game' / 'game.exe')

        wine.write_autorun_cmd(tmp_path, exe.relative_to(tmp_path))

        assert wine.get_game_command(tmp_path) == (exe, [])

    def test_an_existing_autorun_is_kept_as_a_backup(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.cmd').write_text('CMD=old.exe\n')

        wine.write_autorun_cmd(tmp_path, Path('game.exe'))

        assert (tmp_path / 'autorun.cmd.bak').read_text() == 'CMD=old.exe\n'
        assert (tmp_path / 'autorun.cmd').read_text() == 'DIR=.\nCMD="game.exe"\n'


class TestAutorunInfCommand:
    def test_no_autorun_inf_gives_nothing(self, tmp_path: Path) -> None:
        _exe(tmp_path / 'setup.exe')

        assert wine.autorun_inf_command(tmp_path) is None

    def test_open_names_the_installer(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_text('[autorun]\r\nopen=setup.exe\r\nicon=setup.exe\r\n')
        _exe(tmp_path / 'setup.exe')

        assert wine.autorun_inf_command(tmp_path) == ['d:\\setup.exe']

    def test_iso9660_case_and_version_suffix_are_matched(self, tmp_path: Path) -> None:
        (tmp_path / 'AUTORUN.INF;1').write_text('[autorun]\r\nopen=setup.exe\r\n')
        _exe(tmp_path / 'SETUP.EXE;1')

        assert wine.autorun_inf_command(tmp_path) == ['d:\\SETUP.EXE;1']

    def test_a_subdirectory_and_arguments_are_kept(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_text('[autorun]\r\nOPEN=Install\\setup.exe /AUTO\r\n')
        _exe(tmp_path / 'Install' / 'setup.exe')

        assert wine.autorun_inf_command(tmp_path) == ['d:\\Install\\setup.exe', '/AUTO']

    def test_the_architecture_section_wins(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_text(
            '[autorun]\r\nopen=setup32.exe\r\n[autorun.amd64]\r\nopen=setup64.exe\r\n'
        )
        _exe(tmp_path / 'setup32.exe')
        _exe(tmp_path / 'setup64.exe')

        assert wine.autorun_inf_command(tmp_path) == ['d:\\setup64.exe']

    def test_shellexecute_is_used_when_there_is_no_open(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_text('[autorun]\r\nshellexecute=start.exe\r\n')
        _exe(tmp_path / 'start.exe')

        assert wine.autorun_inf_command(tmp_path) == ['d:\\start.exe']

    def test_a_utf16_file_with_a_quoted_path_is_read(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_bytes('[autorun]\r\nopen="My App\\setup.exe" -q\r\n'.encode('utf-16'))
        _exe(tmp_path / 'My App' / 'setup.exe')

        assert wine.autorun_inf_command(tmp_path) == ['d:\\My App\\setup.exe', '-q']

    def test_naming_something_absent_gives_nothing(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_text('[autorun]\r\nopen=nothere.exe\r\n')

        assert wine.autorun_inf_command(tmp_path) is None

    def test_a_file_without_an_autorun_section_gives_nothing(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_text('[something]\r\nopen=setup.exe\r\n')
        _exe(tmp_path / 'setup.exe')

        assert wine.autorun_inf_command(tmp_path) is None

    def test_the_drive_letter_is_configurable(self, tmp_path: Path) -> None:
        (tmp_path / 'autorun.inf').write_text('[autorun]\r\nopen=setup.exe\r\n')
        _exe(tmp_path / 'setup.exe')

        assert wine.autorun_inf_command(tmp_path, 'e:') == ['e:\\setup.exe']


class TestLinkSaves:
    def test_without_either_key_nothing_is_created(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'rom', 'CMD=game.exe\n')
        saves = tmp_path / 'saves'

        wine.link_saves(rom, tmp_path / 'prefix', saves)

        assert not saves.exists()

    def test_a_savedir_is_moved_out_and_linked(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'rom', 'CMD=game.exe\nSAVEDIR=drive_c/game/saves\n')
        prefix = tmp_path / 'prefix'
        target = prefix / 'drive_c' / 'game' / 'saves'
        target.mkdir(parents=True)
        (target / 'a.sav').write_text('x')
        saves = tmp_path / 'saves'

        wine.link_saves(rom, prefix, saves)

        assert target.is_symlink()
        assert target.readlink() == saves
        assert (saves / 'a.sav').read_text() == 'x'

    def test_an_existing_link_is_left_alone(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'rom', 'CMD=game.exe\nSAVEDIR=drive_c/game/saves\n')
        prefix = tmp_path / 'prefix'
        saves = tmp_path / 'saves'
        saves.mkdir()
        target = prefix / 'drive_c' / 'game' / 'saves'
        target.parent.mkdir(parents=True)
        target.symlink_to(saves)

        wine.link_saves(rom, prefix, saves)

        assert target.readlink() == saves

    def test_savefiles_are_moved_out_and_linked(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'rom', 'CMD=game.exe\nSAVEFILES=drive_c/game/a.dat;drive_c/game/b.dat\n')
        prefix = tmp_path / 'prefix'
        existing = prefix / 'drive_c' / 'game' / 'a.dat'
        existing.parent.mkdir(parents=True)
        existing.write_text('kept')
        saves = tmp_path / 'saves'

        wine.link_saves(rom, prefix, saves)

        assert existing.is_symlink()
        assert (saves / 'a.dat').read_text() == 'kept'
        assert (prefix / 'drive_c' / 'game' / 'b.dat').is_symlink()

    def test_running_twice_is_harmless(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'rom', 'CMD=game.exe\nSAVEFILES=drive_c/game/a.dat\n')
        prefix = tmp_path / 'prefix'
        saves = tmp_path / 'saves'

        wine.link_saves(rom, prefix, saves)
        wine.link_saves(rom, prefix, saves)

        assert (prefix / 'drive_c' / 'game' / 'a.dat').readlink() == saves / 'a.dat'


class TestPrefixArch:
    def test_an_unbuilt_prefix_has_no_arch(self, tmp_path: Path) -> None:
        assert wine.current_prefix_arch(tmp_path / 'nothere.wine') is None

    def test_a_registry_without_the_key_has_no_arch(self, tmp_path: Path) -> None:
        (tmp_path / 'userdef.reg').write_text('WINE REGISTRY Version 2\n')

        assert wine.current_prefix_arch(tmp_path) is None

    @pytest.mark.parametrize('arch', ['win32', 'win64'])
    def test_the_recorded_arch_is_read(self, tmp_path: Path, arch: str) -> None:
        (tmp_path / 'userdef.reg').write_text(f'WINE REGISTRY Version 2\n#arch={arch}\n')

        assert wine.current_prefix_arch(tmp_path) == arch


class TestWantedPrefixArch:
    """What the settings ask for. Nothing here looks at a prefix: reconciling the request
    with a prefix that already exists is Runner's job, see test_wine_runner.py."""

    def test_nothing_asked_builds_the_default(self) -> None:
        assert wine.wanted_prefix_arch('wine-tkg') is None

    def test_the_setting_asks_for_win32(self) -> None:
        assert wine.wanted_prefix_arch('wine-tkg', enable_win32=True) == 'win32'

    @pytest.mark.parametrize('runner', ['win32-wine-9.0', 'win32_wine', 'WIN32.wine'])
    def test_a_runner_carrying_win32_asks_for_it(self, runner: str) -> None:
        assert wine.wanted_prefix_arch(runner) == 'win32'

    def test_a_runner_merely_starting_with_win32_does_not(self) -> None:
        assert wine.wanted_prefix_arch('win32wine') is None

    def test_the_reason_for_asking_is_given(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.wanted_prefix_arch('wine-tkg', enable_win32=True)

        assert 'enable_win32 is on' in caplog.text

    def test_and_so_is_the_runner_that_asked(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.wanted_prefix_arch('win32-wine-tkg')

        assert 'carries win32 in its name' in caplog.text


class TestGetRunner:
    def test_an_empty_name_is_the_default_runner(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')

        assert wine.get_runner_name('') == 'wine-tkg'
        assert wine.get_runner_path('') == tmp_path / 'usr' / 'wine-tkg'

    def test_a_shipped_runner_is_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / 'usr' / 'wine-proton').mkdir(parents=True)
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')

        assert wine.get_runner_name('wine-proton') == 'wine-proton'
        assert wine.get_runner_path('wine-proton') == tmp_path / 'usr' / 'wine-proton'

    def test_a_custom_runner_is_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / 'custom' / 'wine-9.22-amd64').mkdir(parents=True)
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')
        monkeypatch.setattr(wine, '_CUSTOM_RUNNERS', tmp_path / 'custom')

        assert wine.get_runner_name('wine-9.22-amd64') == 'wine-9.22-amd64'
        assert wine.get_runner_path('wine-9.22-amd64') == tmp_path / 'custom' / 'wine-9.22-amd64'

    def test_a_missing_runner_falls_back(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')
        monkeypatch.setattr(wine, '_CUSTOM_RUNNERS', tmp_path / 'custom')

        assert wine.get_runner_name('nothere') == 'wine-tkg'
        assert wine.get_runner_path('nothere') == tmp_path / 'usr' / 'wine-tkg'

    def test_the_shipped_runner_wins_over_a_custom_one_of_the_same_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (tmp_path / 'usr' / 'wine-proton').mkdir(parents=True)
        (tmp_path / 'custom' / 'wine-proton').mkdir(parents=True)
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')
        monkeypatch.setattr(wine, '_CUSTOM_RUNNERS', tmp_path / 'custom')

        assert wine.get_runner_path('wine-proton') == tmp_path / 'usr' / 'wine-proton'

    @pytest.mark.parametrize(('name', 'expected'), [('lutris', 'wine-tkg'), ('proton', 'wine-proton')])
    def test_the_old_names_still_work(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, expected: str
    ) -> None:
        (tmp_path / 'usr' / expected).mkdir(parents=True)
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')

        assert wine.get_runner_name(name) == expected


class TestGetPrefixPath:
    def test_a_wine_rom_runs_in_itself(self, tmp_path: Path) -> None:
        rom = tmp_path / 'Game.wine'
        rom.mkdir()

        assert wine.get_prefix_path('windows', 'wine-tkg', rom) == rom

    def test_a_mounted_prefix_is_recognised_by_its_registry(self, tmp_path: Path) -> None:
        rom = tmp_path / 'Game.whatever'
        rom.mkdir()
        (rom / 'system.reg').write_text('WINE REGISTRY Version 2\n')

        assert wine.get_prefix_path('windows', 'wine-tkg', rom) == rom

    def test_anything_else_gets_a_bottle_of_its_own(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine, 'WINE_BOTTLES_DIR', tmp_path / 'bottles')
        rom = tmp_path / 'Game.exe'
        rom.write_text('MZ')

        assert wine.get_prefix_path('windows', 'wine-tkg', rom) == (
            tmp_path / 'bottles' / 'windows' / 'wine-tkg' / 'Game.exe.wine'
        )

    def test_the_bottle_is_kept_per_system_and_runner(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine, 'WINE_BOTTLES_DIR', tmp_path / 'bottles')
        rom = tmp_path / 'Game.pc'
        rom.mkdir()

        assert wine.get_prefix_path('mugen', 'wine-proton', rom) == (
            tmp_path / 'bottles' / 'mugen' / 'wine-proton' / 'Game.pc.wine'
        )


class TestNvidiaPrimeEnvironment:
    @staticmethod
    def _prime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, /, *, laptop: bool) -> None:
        marker = tmp_path / 'nvidia.prime'
        if laptop:
            marker.write_text('pci-0000_01_00_0')
        monkeypatch.setattr(wine, 'Path', _prime_path(marker))

    def test_anything_that_is_not_a_prime_laptop_is_left_as_it_is(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        self._prime(monkeypatch, tmp_path, laptop=False)

        assert wine.nvidia_prime_environment() == {}

    def test_the_game_is_pointed_at_both_nvidia_drivers(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        self._prime(monkeypatch, tmp_path, laptop=True)

        environment = wine.nvidia_prime_environment()

        # a game running in a prefix may be 32bit
        assert 'nvidia_icd.x86_64.json' in str(environment['VK_ICD_FILENAMES'])
        assert 'nvidia_icd.i686.json' in str(environment['VK_ICD_FILENAMES'])
        assert environment['VK_DRIVER_FILES'] == environment['VK_ICD_FILENAMES']

    def test_the_glx_offload_of_the_session_is_dropped(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        self._prime(monkeypatch, tmp_path, laptop=True)
        for variable in ('__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME'):
            monkeypatch.setenv(variable, 'set by the session')

        environment = wine.nvidia_prime_environment()

        assert '__NV_PRIME_RENDER_OFFLOAD' not in os.environ
        assert '__VK_LAYER_NV_optimus' not in os.environ
        assert '__GLX_VENDOR_LIBRARY_NAME' not in os.environ
        assert not any(variable.startswith('__') for variable in environment)


def _fake_mountinfo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, table: str, /) -> None:
    proc = tmp_path / 'proc'
    (proc / 'self').mkdir(parents=True, exist_ok=True)
    (proc / 'self' / 'mountinfo').write_text(table)
    monkeypatch.setattr(wine, '_PROC', proc)


class TestFindPathMount:
    @staticmethod
    def _mountinfo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *lines: str) -> None:
        _fake_mountinfo(tmp_path, monkeypatch, ''.join(f'{line}\n' for line in lines))

    def test_the_deepest_mount_wins(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        deep = tmp_path / 'userdata' / 'roms'
        deep.mkdir(parents=True)
        self._mountinfo(
            tmp_path,
            monkeypatch,
            '1 0 8:1 / / rw,relatime shared:1 - ext4 /dev/sda1 rw',
            f'2 1 8:2 / {tmp_path / "userdata"} rw,relatime shared:2 - btrfs /dev/sda2 rw',
            f'3 2 0:33 / {deep} rw,relatime - overlay overlay rw',
        )

        assert wine.find_path_mount(deep) == ('overlay', deep, 'overlay')

    def test_a_path_falls_back_to_its_parent_mount(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self._mountinfo(
            tmp_path,
            monkeypatch,
            '1 0 8:1 / / rw,relatime - ext4 /dev/sda1 rw',
            f'2 1 8:2 / {tmp_path} rw,relatime - vfat /dev/sdb1 rw',
        )
        game = tmp_path / 'roms' / 'windows' / 'Game.wine'
        game.mkdir(parents=True)

        assert wine.find_path_mount(game) == ('vfat', tmp_path, '/dev/sdb1')

    def test_a_path_that_is_not_there_yet_reports_where_it_would_go(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._mountinfo(tmp_path, monkeypatch, f'1 0 8:1 / {tmp_path} rw - ext4 /dev/sda1 rw')

        assert wine.find_path_mount(tmp_path / 'not' / 'built' / 'yet.wine') == ('ext4', tmp_path, '/dev/sda1')

    def test_escaped_mount_points_are_decoded(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        share = tmp_path / 'my share'
        share.mkdir()
        escaped = str(share).replace(' ', r'\040')
        self._mountinfo(
            tmp_path,
            monkeypatch,
            '1 0 8:1 / / rw - ext4 /dev/sda1 rw',
            f'2 1 0:40 / {escaped} rw - cifs //nas/share rw',
        )

        assert wine.find_path_mount(share) == ('cifs', share, '//nas/share')

    def test_an_unreadable_table_gives_nothing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine, '_PROC', tmp_path / 'nothere')

        assert wine.find_path_mount(tmp_path) is None


class TestLogFilesystems:
    def test_a_directory_is_reported_once_per_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        _fake_mountinfo(tmp_path, monkeypatch, f'1 0 8:1 / {tmp_path} rw - ext4 /dev/sda1 rw\n')
        prefix = tmp_path / 'Game.wine'
        prefix.mkdir()

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.log_filesystems(prefix, prefix)

        assert caplog.text.count(str(prefix)) == 1
        assert 'ext4' in caplog.text

    def test_a_broken_link_is_called_out(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        link = tmp_path / 'broken'
        link.symlink_to(tmp_path / 'nowhere')

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.log_filesystems(link)

        assert 'is a link to' in caplog.text
        assert 'not there' in caplog.text

    def test_a_link_reports_its_target(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        real = tmp_path / 'real'
        real.mkdir()
        link = tmp_path / 'link'
        link.symlink_to(real)

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.log_filesystems(link)

        assert 'linked to' in caplog.text


class TestPrefixHolders:
    @staticmethod
    def _process(proc: Path, pid: int, *environ: str, exe: Path | None = None) -> None:
        entry = proc / str(pid)
        entry.mkdir(parents=True)
        (entry / 'environ').write_bytes(b'\0'.join(record.encode() for record in environ) + b'\0')
        if exe is not None:
            (entry / 'exe').symlink_to(exe)

    def test_a_process_in_the_prefix_is_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        proc = tmp_path / 'proc'
        prefix = tmp_path / 'Game.wine'
        self._process(proc, 10, 'HOME=/userdata/system', f'WINEPREFIX={prefix}')
        self._process(proc, 11, 'HOME=/userdata/system')
        (proc / 'notapid').mkdir()
        monkeypatch.setattr(wine, '_PROC', proc)

        assert wine.prefix_holders(prefix) == [10]

    def test_a_prefix_whose_name_merely_starts_the_same_is_not_matched(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        proc = tmp_path / 'proc'
        prefix = tmp_path / 'Game.wine'
        self._process(proc, 10, f'WINEPREFIX={prefix}-other')
        monkeypatch.setattr(wine, '_PROC', proc)

        assert wine.prefix_holders(prefix) == []

    def test_our_own_process_is_never_held_against_us(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        proc = tmp_path / 'proc'
        prefix = tmp_path / 'Game.wine'
        self._process(proc, os.getpid(), f'WINEPREFIX={prefix}')
        monkeypatch.setattr(wine, '_PROC', proc)

        assert wine.prefix_holders(prefix) == []

    def test_running_prefixes_pairs_a_prefix_with_its_wineserver(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        proc = tmp_path / 'proc'
        prefix = tmp_path / 'Game.wine'
        wineserver = tmp_path / 'bin' / 'wineserver'
        wineserver.parent.mkdir(parents=True)
        wineserver.write_text('')
        self._process(proc, 10, f'WINEPREFIX={prefix}', exe=wineserver)
        monkeypatch.setattr(wine, '_PROC', proc)

        assert wine.running_prefixes() == {prefix: wineserver}

    def test_a_prefix_without_a_wineserver_is_still_reported(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        proc = tmp_path / 'proc'
        prefix = tmp_path / 'Game.wine'
        self._process(proc, 10, f'WINEPREFIX={prefix}')
        monkeypatch.setattr(wine, '_PROC', proc)

        assert wine.running_prefixes() == {prefix: None}
