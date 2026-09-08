from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from batocera_launch import BatoceraException
from batocera_launch_wine import wine

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def _recording(into: list[Any], /) -> Callable[..., None]:
    def record(*args: object) -> None:
        into.append(args)

    return record


def _recording_first(into: list[Any], /) -> Callable[..., None]:
    def record(first: object, /, **kwargs: object) -> None:
        into.append(first)

    return record


def _recording_environment(into: list[Any], /) -> Callable[..., None]:
    def record(cmd: object, /, **kwargs: Any) -> None:
        into.append(kwargs.get('environment'))

    return record


def _local_display() -> dict[str, str]:
    return {'DISPLAY': ':9'}


def _touch(path: Path, content: str = '') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


@pytest.fixture
def user_wine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    directory = tmp_path / 'system' / 'wine'
    directory.mkdir(parents=True)
    monkeypatch.setattr(wine, 'USER_WINE_DIR', directory)
    monkeypatch.setattr(wine, '_IMPORT_LOG', directory / 'imports.log')
    monkeypatch.setattr(wine, '_USER_DXVK_DIR', directory / 'dxvk')
    monkeypatch.setattr(wine, '_SYSTEM_DXVK_DIR', tmp_path / 'usr' / 'wine' / 'dxvk')
    return directory


@pytest.fixture
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> wine.Runner:
    base = tmp_path / 'usr' / 'wine'
    root = base / 'wine-tkg'
    for tool in ('wine', 'wineserver', 'msiexec'):
        _touch(root / 'bin' / tool)
    _touch(root / 'lib' / 'wine' / 'i386-unix' / 'wine')
    _touch(root / 'lib' / 'wine' / 'x86_64-unix' / 'wine64')
    monkeypatch.setattr(wine, 'WINE_BASE', base)
    monkeypatch.setattr(wine, '_CUSTOM_RUNNERS', tmp_path / 'custom')

    prefix = tmp_path / 'Game.wine'
    prefix.mkdir()

    return wine.Runner('wine-tkg', prefix=prefix)


class _Recorder:
    def __init__(self) -> None:
        self.commands: list[list[Any]] = []

    def __call__(self, cmd: Any, **kwargs: Any) -> None:
        self.commands.append(list(cmd))


@pytest.fixture
def ran(runner: wine.Runner, monkeypatch: pytest.MonkeyPatch) -> _Recorder:
    recorder = _Recorder()
    monkeypatch.setattr(runner, 'run_in_prefix', recorder)
    return recorder


class TestInstallDxvk:
    def test_the_shipped_build_is_linked_into_both_windows_directories(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        dxvk = tmp_path / 'usr' / 'wine' / 'dxvk'
        _touch(dxvk / 'x64' / 'd3d11.dll')
        _touch(dxvk / 'x32' / 'd3d9.dll')

        assert runner.install_dxvk() == ['d3d11,d3d9=n']

        system32 = runner.prefix_dir / 'drive_c' / 'windows' / 'system32' / 'd3d11.dll'
        syswow64 = runner.prefix_dir / 'drive_c' / 'windows' / 'syswow64' / 'd3d9.dll'

        assert system32.readlink() == dxvk / 'x64' / 'd3d11.dll'
        assert syswow64.readlink() == dxvk / 'x32' / 'd3d9.dll'

    def test_a_user_build_replaces_the_shipped_one(self, runner: wine.Runner, user_wine: Path, tmp_path: Path) -> None:
        _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x64' / 'd3d11.dll')
        _touch(user_wine / 'dxvk' / 'x64' / 'd3d11.dll')

        runner.install_dxvk()

        linked = (runner.prefix_dir / 'drive_c' / 'windows' / 'system32' / 'd3d11.dll').readlink()

        assert linked == user_wine / 'dxvk' / 'x64' / 'd3d11.dll'

    def test_only_what_is_really_there_is_linked(self, runner: wine.Runner, user_wine: Path, tmp_path: Path) -> None:
        _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x64' / 'd3d11.dll')

        runner.install_dxvk()

        system32 = runner.prefix_dir / 'drive_c' / 'windows' / 'system32'

        assert [p.name for p in system32.iterdir()] == ['d3d11.dll']
        assert all(p.exists() for p in system32.iterdir())

    def test_a_missing_dxvk_links_nothing(self, runner: wine.Runner, user_wine: Path) -> None:
        assert runner.install_dxvk() == []

    def test_wine_own_dll_is_replaced_rather_than_kept(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        builtin = _touch(runner.prefix_dir / 'drive_c' / 'windows' / 'system32' / 'd3d11.dll', 'builtin')
        _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x64' / 'd3d11.dll')

        runner.install_dxvk()

        assert builtin.is_symlink()


class TestInstallBuiltinD3d:
    def test_the_direct3d_dlls_of_wine_are_put_back(self, runner: wine.Runner, tmp_path: Path) -> None:
        shared = tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'lib' / 'wine'
        _touch(shared / 'x86_64-windows' / 'd3d11.dll')
        _touch(shared / 'i386-windows' / 'd3d9.dll')

        assert runner.install_builtin_d3d() == {'d3d11', 'd3d9'}

    def test_a_stale_dxvk_link_is_replaced(self, runner: wine.Runner, tmp_path: Path) -> None:
        shared = tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'lib' / 'wine'
        builtin = _touch(shared / 'x86_64-windows' / 'd3d11.dll')
        stale = runner.prefix_dir / 'drive_c' / 'windows' / 'system32' / 'd3d11.dll'
        stale.parent.mkdir(parents=True)
        stale.symlink_to(tmp_path / 'gone' / 'd3d11.dll')

        runner.install_builtin_d3d()

        assert stale.readlink() == builtin

    def test_dlls_that_are_not_direct3d_are_left_alone(self, runner: wine.Runner, tmp_path: Path) -> None:
        shared = tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'lib' / 'wine'
        _touch(shared / 'x86_64-windows' / 'kernel32.dll')

        assert runner.install_builtin_d3d() == set()

    def test_nothing_to_link_gives_nothing(self, runner: wine.Runner) -> None:
        assert runner.install_builtin_d3d() == set()


class TestRunnerDlls:
    """
    ge-proton is built differently than wine-tkg or wine-proton: it splits lib and
    lib64 and keeps the direct3d and the libraries it ships in directories of their own.
    """

    @staticmethod
    def _component(tmp_path: Path, component: str, arch: str, *names: str) -> Path:
        directory = tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'lib' / component / arch
        for name in names:
            _touch(directory / name)
        return directory

    def test_the_dxvk_of_the_runner_is_used_over_the_one_of_batocera(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x64' / 'd3d11.dll')
        runner_dxvk = self._component(tmp_path, 'dxvk', 'x86_64-windows', 'd3d11.dll')

        assert runner.install_dxvk() == ['d3d11=n']
        assert (runner.prefix_dir / 'drive_c' / 'windows' / 'system32' / 'd3d11.dll').readlink() == (
            runner_dxvk / 'd3d11.dll'
        )

    def test_d3d12_and_nvapi_come_from_beside_it(self, runner: wine.Runner, user_wine: Path, tmp_path: Path) -> None:
        self._component(tmp_path, 'dxvk', 'x86_64-windows', 'd3d11.dll')
        self._component(tmp_path, 'vkd3d-proton', 'x86_64-windows', 'd3d12.dll')
        self._component(tmp_path, 'nvapi', 'i386-windows', 'nvapi.dll')

        assert runner.install_dxvk() == ['d3d11,d3d12=n', 'nvapi=']

    def test_a_runner_shipping_none_falls_back_to_batocera(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        shipped = _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x64' / 'd3d11.dll')

        assert runner.install_dxvk() == ['d3d11=n']
        assert (runner.prefix_dir / 'drive_c' / 'windows' / 'system32' / 'd3d11.dll').readlink() == shipped

    def test_the_dxvk_is_what_decides_whose_direct3d_is_used(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        # a runner shipping nvapi alone still draws through the dxvk of batocera
        shipped = _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x64' / 'd3d11.dll')
        self._component(tmp_path, 'nvapi', 'x86_64-windows', 'nvapi64.dll')

        assert runner.install_dxvk() == ['d3d11=n']
        assert (runner.prefix_dir / 'drive_c' / 'windows' / 'system32' / 'd3d11.dll').readlink() == shipped

    def test_vkd3d_and_icu_are_linked_into_the_prefix(self, runner: wine.Runner, tmp_path: Path) -> None:
        vkd3d = self._component(tmp_path, 'vkd3d', 'x86_64-windows', 'libvkd3d-1.dll')
        icu = self._component(tmp_path, 'icu', 'i386-windows', 'icuuc.dll')

        runner.install_runner_libs()

        windows = runner.prefix_dir / 'drive_c' / 'windows'

        assert (windows / 'system32' / 'libvkd3d-1.dll').readlink() == vkd3d / 'libvkd3d-1.dll'
        assert (windows / 'syswow64' / 'icuuc.dll').readlink() == icu / 'icuuc.dll'

    def test_nvapi_is_loaded_only_when_the_game_may_reach_the_driver(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        self._component(tmp_path, 'dxvk', 'x86_64-windows', 'd3d11.dll', 'nvapi64.dll')

        assert runner.install_dxvk() == ['d3d11=n', 'nvapi64=']
        assert runner.install_dxvk(nvapi=True) == ['d3d11=n', 'nvapi64=n']

    def test_a_runner_without_them_links_nothing(self, runner: wine.Runner) -> None:
        runner.install_runner_libs()

        assert not (runner.prefix_dir / 'drive_c' / 'windows' / 'system32').exists()

    def test_the_fonts_of_the_runner_are_copied_in(self, runner: wine.Runner, user_wine: Path, tmp_path: Path) -> None:
        _touch(tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'share' / 'fonts' / 'arial.ttf', 'runner')

        runner.install_fonts()

        copied = runner.prefix_dir / 'drive_c' / 'windows' / 'Fonts' / 'arial.ttf'

        # the prefix outlives the runner, so it holds a font rather than a link into one
        assert not copied.is_symlink()
        assert copied.read_text() == 'runner'

    def test_a_link_left_by_an_older_prefix_becomes_a_font_of_its_own(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        font = _touch(tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'share' / 'fonts' / 'arial.ttf', 'runner')
        stale = runner.prefix_dir / 'drive_c' / 'windows' / 'Fonts' / 'arial.ttf'
        stale.parent.mkdir(parents=True)
        stale.symlink_to(font)

        runner.install_fonts()

        assert not stale.is_symlink()
        assert stale.read_text() == 'runner'

    def test_a_font_the_user_installed_is_left_alone(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        _touch(tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'share' / 'fonts' / 'arial.ttf', 'runner')
        theirs = _touch(runner.prefix_dir / 'drive_c' / 'windows' / 'Fonts' / 'arial.ttf', 'theirs')

        runner.install_fonts()

        assert theirs.read_text() == 'theirs'


class TestInstallD7vk:
    def test_the_ddraw_of_the_runner_is_preferred(self, runner: wine.Runner, user_wine: Path, tmp_path: Path) -> None:
        d7vk = _touch(tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'lib' / 'd7vk' / 'i386-windows' / 'ddraw.dll')

        assert runner.install_d7vk(True) is True
        assert (runner.prefix_dir / 'drive_c' / 'windows' / 'syswow64' / 'ddraw.dll').readlink() == d7vk

    def test_the_build_of_batocera_is_the_fallback(self, runner: wine.Runner, user_wine: Path, tmp_path: Path) -> None:
        shipped = _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x32' / 'ddraw.dll')

        assert runner.install_d7vk(True) is True
        assert (runner.prefix_dir / 'drive_c' / 'windows' / 'syswow64' / 'ddraw.dll').readlink() == shipped

    def test_the_ddraw_of_wine_is_kept_beside_it(self, runner: wine.Runner, user_wine: Path, tmp_path: Path) -> None:
        _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x32' / 'ddraw.dll')
        builtin = _touch(tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'lib' / 'wine' / 'i386-windows' / 'ddraw.dll')

        runner.install_d7vk(True)

        assert (runner.prefix_dir / 'drive_c' / 'windows' / 'syswow64' / 'ddraw_.dll').readlink() == builtin

    def test_turning_it_off_puts_the_ddraw_of_wine_back(
        self, runner: wine.Runner, user_wine: Path, tmp_path: Path
    ) -> None:
        _touch(tmp_path / 'usr' / 'wine' / 'dxvk' / 'x32' / 'ddraw.dll')
        builtin = _touch(tmp_path / 'usr' / 'wine' / 'wine-tkg' / 'lib' / 'wine' / 'i386-windows' / 'ddraw.dll')
        runner.install_d7vk(True)

        assert runner.install_d7vk(False) is False

        syswow64 = runner.prefix_dir / 'drive_c' / 'windows' / 'syswow64'

        assert (syswow64 / 'ddraw.dll').readlink() == builtin
        assert not (syswow64 / 'ddraw_.dll').exists()

    def test_asking_for_a_d7vk_that_is_not_there_leaves_wine_to_it(self, runner: wine.Runner, user_wine: Path) -> None:
        assert runner.install_d7vk(True) is False


class TestSandboxPrefix:
    def test_a_linked_user_directory_becomes_a_real_one(self, runner: wine.Runner, tmp_path: Path) -> None:
        outside = tmp_path / 'outside'
        outside.mkdir()
        documents = runner.prefix_dir / 'drive_c' / 'users' / 'root' / 'Documents'
        documents.parent.mkdir(parents=True)
        documents.symlink_to(outside)

        runner.sandbox_prefix()

        assert documents.is_dir()
        assert not documents.is_symlink()

    def test_every_user_of_the_prefix_is_covered(self, runner: wine.Runner, tmp_path: Path) -> None:
        outside = tmp_path / 'outside'
        outside.mkdir()
        users = runner.prefix_dir / 'drive_c' / 'users'
        for user in ('root', 'steamuser'):
            directory = users / user / 'Music'
            directory.parent.mkdir(parents=True)
            directory.symlink_to(outside)

        runner.sandbox_prefix()

        assert not (users / 'root' / 'Music').is_symlink()
        assert not (users / 'steamuser' / 'Music').is_symlink()

    def test_a_real_directory_is_left_as_it_is(self, runner: wine.Runner) -> None:
        documents = runner.prefix_dir / 'drive_c' / 'users' / 'root' / 'Documents'
        documents.mkdir(parents=True)
        (documents / 'save.dat').write_text('kept')

        runner.sandbox_prefix()

        assert (documents / 'save.dat').read_text() == 'kept'

    def test_directories_wine_did_not_create_are_not_invented(self, runner: wine.Runner) -> None:
        user = runner.prefix_dir / 'drive_c' / 'users' / 'root'
        user.mkdir(parents=True)

        runner.sandbox_prefix()

        assert list(user.iterdir()) == []

    def test_a_prefix_without_users_is_no_trouble(self, runner: wine.Runner) -> None:
        runner.sandbox_prefix()


class TestImportDirectories:
    def test_a_redist_is_run_and_moved_aside(self, runner: wine.Runner, user_wine: Path, ran: _Recorder) -> None:
        installer = _touch(user_wine / 'exe' / 'something.exe')

        runner.install_redists()

        assert ran.commands == [[runner.wine, installer]]
        assert not installer.exists()
        assert (user_wine / 'installed.exe' / 'something.exe').exists()

    @pytest.mark.parametrize(
        ('name', 'arguments'),
        [
            ('dxsetup.exe', ['/silent']),
            ('vcredist_x64_2005.exe', ['/q']),
            ('vcredist_x86_2008.exe', ['/q']),
            ('vcredist_x64_2022.exe', ['/quiet', '/qn', '/norestart']),
            ('oalinst.exe', ['/s']),
            ('anything.exe', []),
        ],
    )
    def test_each_redist_gets_the_arguments_it_wants(
        self, runner: wine.Runner, user_wine: Path, ran: _Recorder, name: str, arguments: list[str]
    ) -> None:
        installer = _touch(user_wine / 'exe' / name)

        runner.install_redists()

        assert ran.commands == [[runner.wine, installer, *arguments]]

    def test_what_is_imported_is_written_to_the_log(self, runner: wine.Runner, user_wine: Path, ran: _Recorder) -> None:
        _touch(user_wine / 'exe' / 'something.exe')

        runner.install_redists()

        assert 'something.exe' in (user_wine / 'imports.log').read_text()

    def test_a_second_import_of_the_same_name_is_kept_too(
        self, runner: wine.Runner, user_wine: Path, ran: _Recorder
    ) -> None:
        _touch(user_wine / 'installed.exe' / 'something.exe', 'first')
        _touch(user_wine / 'exe' / 'something.exe', 'second')

        runner.install_redists()

        kept = sorted(p.name for p in (user_wine / 'installed.exe').iterdir())

        assert len(kept) == 2
        assert (user_wine / 'installed.exe' / 'something.exe').read_text() == 'first'

    def test_an_msi_is_installed_quietly(self, runner: wine.Runner, user_wine: Path, ran: _Recorder) -> None:
        package = _touch(user_wine / 'msi' / 'thing.msi')

        runner.install_msis()

        assert ran.commands == [[runner.msiexec, '-i', package, '/quiet', '/qn', '/norestart']]

    def test_a_font_is_copied_into_the_prefix(self, runner: wine.Runner, user_wine: Path) -> None:
        _touch(user_wine / 'fonts' / 'thing.ttf', 'font')

        runner.install_fonts()

        assert (runner.prefix_dir / 'drive_c' / 'windows' / 'Fonts' / 'thing.ttf').read_text() == 'font'

    def test_only_the_wanted_suffixes_are_taken(self, runner: wine.Runner, user_wine: Path, ran: _Recorder) -> None:
        _touch(user_wine / 'exe' / 'readme.txt')

        runner.install_redists()

        assert ran.commands == []
        assert (user_wine / 'exe' / 'readme.txt').exists()

    def test_an_empty_import_directory_is_tidied_away(
        self, runner: wine.Runner, user_wine: Path, ran: _Recorder
    ) -> None:
        (user_wine / 'exe').mkdir()

        runner.install_redists()

        assert not (user_wine / 'exe').exists()

    def test_no_import_directory_at_all_is_fine(self, runner: wine.Runner, user_wine: Path, ran: _Recorder) -> None:
        runner.install_redists()
        runner.install_msis()
        runner.install_regs()
        runner.install_fonts()

        assert ran.commands == []


class TestRegistry:
    def test_a_registry_file_is_imported_into_both_architectures(
        self, runner: wine.Runner, tmp_path: Path, ran: _Recorder
    ) -> None:
        registry = _touch(tmp_path / 'thing.reg')

        runner.regedit(registry)

        assert len(ran.commands) == 2
        assert all(f'//?/unix{registry}' in command for command in ran.commands)

    def test_a_rawinput_file_is_imported_and_consumed(
        self, runner: wine.Runner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ran: _Recorder
    ) -> None:
        rawinput = _touch(tmp_path / 'rawinput.reg')
        monkeypatch.setattr(wine, '_RAWINPUT_REG', rawinput)

        runner.install_rawinput()

        assert ran.commands
        assert not rawinput.exists()

    def test_without_a_rawinput_file_nothing_happens(
        self, runner: wine.Runner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ran: _Recorder
    ) -> None:
        monkeypatch.setattr(wine, '_RAWINPUT_REG', tmp_path / 'nothere.reg')

        runner.install_rawinput()

        assert ran.commands == []


class TestHidraw:
    def test_it_is_written_when_the_prefix_says_nothing(
        self, runner: wine.Runner, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        written: list[tuple[str, ...]] = []
        monkeypatch.setattr(runner, 'set_registry_value', _recording(written))

        runner.set_hidraw(True)

        assert written
        assert written[0][-1] == '0'

    def test_it_is_not_written_again_when_already_set(
        self, runner: wine.Runner, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (runner.prefix_dir / 'system.reg').write_text('"DisableHidraw"=dword:00000001\n')
        written: list[tuple[str, ...]] = []
        monkeypatch.setattr(runner, 'set_registry_value', _recording(written))

        runner.set_hidraw(False)

        assert written == []

    def test_turning_it_on_over_an_existing_off_rewrites_it(
        self, runner: wine.Runner, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (runner.prefix_dir / 'system.reg').write_text('"DisableHidraw"=dword:00000001\n')
        written: list[tuple[str, ...]] = []
        monkeypatch.setattr(runner, 'set_registry_value', _recording(written))

        runner.set_hidraw(True)

        assert written
        assert written[0][-1] == '0'


class TestWinetricks:
    def test_a_missing_winetricks_is_reported(
        self, runner: wine.Runner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(wine, '_WINETRICKS_CMD', tmp_path / 'nothere')

        with pytest.raises(BatoceraException):
            runner.run_winetricks(['-q', 'vcrun2022'])

    def test_a_trick_is_only_applied_once(
        self, runner: wine.Runner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(wine, '_WINETRICKS_CMD', _touch(tmp_path / 'winetricks'))
        applied: list[Any] = []
        monkeypatch.setattr(runner, 'run_winetricks', _recording_first(applied))

        runner.install_wine_trick('vcrun2022')
        runner.install_wine_trick('vcrun2022')

        assert applied == [['-q', 'vcrun2022']]
        assert (runner.prefix_dir / 'vcrun2022.done').exists()

    def test_winetricks_is_given_a_display_when_there_is_none(
        self, runner: wine.Runner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ran: _Recorder
    ) -> None:
        monkeypatch.setattr(wine, '_WINETRICKS_CMD', _touch(tmp_path / 'winetricks'))
        monkeypatch.delenv('DISPLAY', raising=False)
        monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)
        monkeypatch.setattr(wine, 'local_display', _local_display)

        environments: list[Any] = []
        monkeypatch.setattr(runner, 'run_in_prefix', _recording_environment(environments))

        runner.run_winetricks(['-q', 'vcrun2022'])

        assert environments[0]['DISPLAY'] == ':9'

    def test_an_existing_display_is_left_alone(
        self, runner: wine.Runner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(wine, '_WINETRICKS_CMD', _touch(tmp_path / 'winetricks'))
        monkeypatch.setenv('DISPLAY', ':0')

        environments: list[Any] = []
        monkeypatch.setattr(runner, 'run_in_prefix', _recording_environment(environments))

        runner.run_winetricks(['-q', 'vcrun2022'])

        assert 'DISPLAY' not in environments[0]
