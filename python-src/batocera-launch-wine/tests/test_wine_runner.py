from __future__ import annotations

import logging
import os
import resource
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import pytest

from batocera_launch import BatoceraException
from batocera_launch_wine import wine

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_WINE_PATHS = (
    'WINEPREFIX',
    'LD_LIBRARY_PATH',
    'WINEDLLPATH',
    'LIBGL_DRIVERS_PATH',
    'GST_PLUGIN_SYSTEM_PATH_1_0',
    'SPA_PLUGIN_DIR',
    'PIPEWIRE_MODULE_DIR',
)


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('')
    return path


def _runner_tree(
    base: Path,
    name: str = 'wine-tkg',
    /,
    *,
    split_arch: bool = True,
    has_wine64: bool = True,
    split_libs: bool = False,
) -> Path:
    root = base / name

    for tool in ('wine', 'wineserver', 'msiexec'):
        _touch(root / 'bin' / tool)

    if split_arch:
        _touch(root / 'lib' / 'wine' / 'i386-unix' / 'wine')
        if has_wine64:
            _touch(root / 'lib' / 'wine' / 'x86_64-unix' / 'wine64')
    elif has_wine64:
        _touch(root / 'bin' / 'wine64')

    if split_libs:
        (root / 'lib32' / 'wine').mkdir(parents=True)
        (root / 'lib64' / 'wine').mkdir(parents=True)
    else:
        (root / 'lib' / 'wine').mkdir(parents=True, exist_ok=True)

    return root


def _prefix(path: Path, arch: str | None = None) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    if arch:
        (path / 'userdef.reg').write_text(f'WINE REGISTRY Version 2\n#arch={arch}\n')
    return path


@pytest.fixture
def wine_base(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    base = tmp_path / 'usr' / 'wine'
    base.mkdir(parents=True)
    monkeypatch.setattr(wine, 'WINE_BASE', base)
    monkeypatch.setattr(wine, '_CUSTOM_RUNNERS', tmp_path / 'custom')
    monkeypatch.setattr(wine, 'WINE_BOTTLES_DIR', tmp_path / 'bottles')
    return base


def _raising(*args: object) -> None:
    raise OSError('nope')


def _bootstrapping(prefix: Path, /) -> Callable[..., None]:
    """Stands in for the wineboot that would create the registry of a new prefix."""

    def bootstrap(*args: object, **kwargs: object) -> None:
        (prefix / 'system.reg').write_text('WINE REGISTRY Version 2\n')

    return bootstrap


def _recording(into: list[Any], /) -> Callable[..., None]:
    def record(cmd: Sequence[Any], **kwargs: object) -> None:
        into.append(list(cmd))

    return record


def _recording_environment(into: list[Any], /) -> Callable[..., None]:
    def record(cmd: Sequence[Any], **kwargs: Any) -> None:
        into.append(kwargs['environment'])

    return record


def _nothing(*args: object, **kwargs: object) -> None:
    return None


class _FakeProcess:
    returncode = 0

    def communicate(self) -> tuple[bytes, bytes]:
        return b'', b''


class _FailedProcess(_FakeProcess):
    returncode = 1


def _failing(*args: object, **kwargs: object) -> _FakeProcess:
    return _FailedProcess()


class _Calls:
    def __init__(self) -> None:
        self.popen: list[dict[str, Any]] = []
        self.run: list[dict[str, Any]] = []

    def fake_popen(self, cmd: Any, env: Any = None, stdout: Any = None, stderr: Any = None) -> _FakeProcess:
        self.popen.append({'cmd': cmd, 'env': env, 'stdout': stdout})
        return _FakeProcess()

    def fake_run(self, cmd: Any, **kwargs: Any) -> SimpleNamespace:
        self.run.append({'cmd': cmd, **kwargs})
        return SimpleNamespace(returncode=0)


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> _Calls:
    recorded = _Calls()
    monkeypatch.setattr(subprocess, 'Popen', recorded.fake_popen)
    monkeypatch.setattr(subprocess, 'run', recorded.fake_run)
    return recorded


class TestRunnerLayout:
    def test_a_split_arch_build_uses_the_loader_of_each_architecture(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base)

        runner = wine.Runner('wine-tkg', 'bottle')

        assert runner.wine == root / 'lib' / 'wine' / 'i386-unix' / 'wine'
        assert runner.wine64 == root / 'lib' / 'wine' / 'x86_64-unix' / 'wine64'

    def test_a_wow64_only_build_uses_the_single_loader(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base, split_arch=False)

        runner = wine.Runner('wine-tkg', 'bottle')

        assert runner.wine == root / 'bin' / 'wine'
        assert runner.wine64 == root / 'bin' / 'wine64'

    def test_without_a_wine64_it_falls_back_to_wine(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base, split_arch=False, has_wine64=False)

        runner = wine.Runner('wine-tkg', 'bottle')

        assert runner.wine64 == runner.wine == root / 'bin' / 'wine'

    def test_a_split_arch_build_without_wine64_also_falls_back(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base, has_wine64=False)

        runner = wine.Runner('wine-tkg', 'bottle')

        assert runner.wine64 == runner.wine == root / 'lib' / 'wine' / 'i386-unix' / 'wine'

    def test_wine_proton_keeps_its_own_loader_even_with_a_32bit_one_present(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base, 'wine-proton')

        runner = wine.Runner('wine-proton', 'bottle')

        assert runner.wine == root / 'bin' / 'wine'

    def test_the_wineserver_and_msiexec_come_from_bin(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base)

        runner = wine.Runner('wine-tkg', 'bottle')

        assert runner.wineserver == root / 'bin' / 'wineserver'
        assert runner.msiexec == root / 'bin' / 'msiexec'

    def test_split_libraries_are_preferred_when_present(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base, split_libs=True)

        environment = wine.Runner('wine-tkg', 'bottle').get_environment()

        assert environment['WINEDLLPATH'] == (
            f'{root / "lib32" / "wine"}/i386-windows:{root / "lib64" / "wine"}/x86_64-windows'
        )

    def test_otherwise_both_architectures_share_lib_wine(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base)
        shared = root / 'lib' / 'wine'

        environment = wine.Runner('wine-tkg', 'bottle').get_environment()

        assert environment['WINEDLLPATH'] == f'{shared}/i386-windows:{shared}/x86_64-windows'

    def test_the_library_path_names_both_architectures(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base)
        shared = root / 'lib' / 'wine'

        environment = wine.Runner('wine-tkg', 'bottle').get_environment()

        assert environment['LD_LIBRARY_PATH'] == (f'/lib32:{shared}/i386-unix:/lib:/usr/lib:{shared}/x86_64-unix')

    def test_a_named_bottle_lives_under_the_bottles_directory(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        assert wine.Runner('wine-tkg', 'model2').prefix_dir == tmp_path / 'bottles' / 'model2'

    def test_a_prefix_is_used_as_it_stands(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine')

        assert wine.Runner('wine-tkg', prefix=prefix).prefix_dir == prefix

    def test_neither_a_bottle_nor_a_prefix_is_refused(self, wine_base: Path) -> None:
        _runner_tree(wine_base)

        with pytest.raises(BatoceraException):
            wine.Runner('wine-tkg')

    def test_an_unknown_runner_falls_back_to_the_default(self, wine_base: Path) -> None:
        _runner_tree(wine_base)

        assert wine.Runner('nothere', 'bottle').runner_name == 'wine-tkg'


class TestRunnerArch:
    def test_a_fresh_prefix_takes_the_architecture_asked_for(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        runner = wine.Runner('wine-tkg', prefix=tmp_path / 'new.wine', arch='win32')

        assert runner.arch == 'win32'

    def test_an_existing_prefix_keeps_its_own(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine', 'win32')

        assert wine.Runner('wine-tkg', prefix=prefix).arch == 'win32'

    def test_and_a_win32_request_is_dropped_for_it(
        self, wine_base: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine', 'win64')

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            runner = wine.Runner('wine-tkg', prefix=prefix, arch='win32')

        assert runner.arch is None
        assert 'found arch win64' in caplog.text

    def test_a_win64_prefix_is_left_for_wine_to_work_out(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine', 'win64')

        assert 'WINEARCH' not in wine.Runner('wine-tkg', prefix=prefix).get_environment()

    def test_a_win32_prefix_is_named_explicitly(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine', 'win32')

        assert wine.Runner('wine-tkg', prefix=prefix).get_environment()['WINEARCH'] == 'win32'

    def test_the_arch_found_in_the_registry_is_reported(
        self, wine_base: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine', 'win64')

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.Runner('wine-tkg', prefix=prefix)

        assert 'found arch win64' in caplog.text

    def test_a_request_it_cannot_honour_is_a_warning(
        self, wine_base: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine', 'win64')

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.Runner('wine-tkg', prefix=prefix, arch='win32')

        assert 'cannot be turned into a 32bit one' in caplog.text
        assert [r for r in caplog.records if r.levelno >= logging.WARNING]

    def test_an_existing_win32_prefix_draws_no_complaint(
        self, wine_base: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        _runner_tree(wine_base)
        prefix = _prefix(tmp_path / 'Game.wine', 'win32')

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.Runner('wine-tkg', prefix=prefix, arch='win32')

        assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []

    def test_a_fresh_prefix_says_it_is_being_built_win64(
        self, wine_base: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        _runner_tree(wine_base)

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            wine.Runner('wine-tkg', prefix=tmp_path / 'new.wine')

        assert 'building the prefix as win64' in caplog.text

    def test_a_runner_without_win32_mode_builds_win64_instead(
        self, wine_base: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        _runner_tree(wine_base, split_arch=False)

        with caplog.at_level(logging.INFO, logger=wine.__name__):
            runner = wine.Runner('wine-tkg', prefix=tmp_path / 'new.wine', arch='win32')

        assert runner.arch is None
        assert 'has no win32 mode' in caplog.text

    def test_an_existing_win32_prefix_on_such_a_runner_is_refused(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base, split_arch=False)
        prefix = _prefix(tmp_path / 'Game.wine', 'win32')

        with pytest.raises(BatoceraException, match='win32'):
            wine.Runner('wine-tkg', prefix=prefix)

    def test_nothing_asked_leaves_the_architecture_to_wine(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        runner = wine.Runner('wine-tkg', prefix=tmp_path / 'new.wine')

        assert runner.arch is None
        assert 'WINEARCH' not in runner.get_environment()


class TestFileLimit:
    def test_every_runner_raises_it_for_the_wine_it_will_start(
        self, wine_base: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _runner_tree(wine_base)
        wanted: list[tuple[int, int]] = []

        def get_limits(which: int, /) -> tuple[int, int]:
            return (1024, 524288)

        def set_limits(which: int, limits: tuple[int, int], /) -> None:
            wanted.append(limits)

        monkeypatch.setattr(resource, 'getrlimit', get_limits)
        monkeypatch.setattr(resource, 'setrlimit', set_limits)

        wine.Runner('wine-tkg', 'bottle')

        # the hard limit is what caps it, a game may not have as many as we ask for
        assert wanted == [(524288, 524288)]

    def test_a_limit_that_will_not_move_is_not_worth_failing_a_start_over(
        self, wine_base: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _runner_tree(wine_base)
        monkeypatch.setattr(resource, 'setrlimit', _raising)

        assert wine.Runner('wine-tkg', 'bottle').runner_name == 'wine-tkg'


class TestRunnerEnvironment:
    def test_the_game_is_given_every_wine_path(self, wine_base: Path) -> None:
        _runner_tree(wine_base)

        environment = wine.Runner('wine-tkg', 'bottle').get_environment()

        assert set(_WINE_PATHS) <= set(environment)

    def test_pipewire_and_gstreamer_are_exported(self, wine_base: Path) -> None:
        _runner_tree(wine_base)

        environment = wine.Runner('wine-tkg', 'bottle').get_environment()

        assert environment['SPA_PLUGIN_DIR'] == '/usr/lib/spa-0.2:/lib32/spa-0.2'
        assert environment['PIPEWIRE_MODULE_DIR'] == '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3'
        assert environment['GST_PLUGIN_SYSTEM_PATH_1_0'] == '/usr/lib/gstreamer-1.0:/lib32/gstreamer-1.0'

    def test_the_prefix_is_the_bottle(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        environment = wine.Runner('wine-tkg', 'bottle').get_environment()

        assert environment['WINEPREFIX'] == tmp_path / 'bottles' / 'bottle'

    def test_the_game_keeps_the_path_it_was_given(self, wine_base: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        root = _runner_tree(wine_base)
        monkeypatch.setenv('PATH', '/somewhere')

        environment = wine.Runner('wine-tkg', 'bottle').get_environment()

        assert environment['PATH'] == f'{root / "bin"}:/somewhere'

    def test_the_architecture_is_exported_when_there_is_one(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        runner = wine.Runner('wine-tkg', prefix=tmp_path / 'new.wine', arch='win32')

        assert runner.get_environment()['WINEARCH'] == 'win32'

    def test_the_linux_libraries_of_the_runner_are_appended(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base)
        (root / 'lib' / 'x86_64-linux-gnu').mkdir(parents=True)

        library_path = str(wine.Runner('wine-tkg', 'bottle').get_environment()['LD_LIBRARY_PATH'])

        assert library_path.endswith(f'{root / "lib" / "x86_64-linux-gnu"}:{root / "lib" / "i386-linux-gnu"}')

    def test_a_runner_without_them_is_left_as_it_was(self, wine_base: Path) -> None:
        root = _runner_tree(wine_base)

        library_path = str(wine.Runner('wine-tkg', 'bottle').get_environment()['LD_LIBRARY_PATH'])

        assert library_path.endswith(f'{root / "lib" / "wine"}/x86_64-unix')


class TestRunInPrefix:
    def test_a_command_in_the_prefix_gets_the_same_wine_paths_as_the_game(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'], wait=False)

        used = calls.popen[0]['env']
        expected = runner.get_environment()

        for name in _WINE_PATHS:
            assert used[name] == expected[name]

    def test_pipewire_reaches_an_installer_run_in_the_prefix(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'setup.exe'], wait=False)

        assert calls.popen[0]['env']['PIPEWIRE_MODULE_DIR'] == '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3'

    def test_the_runner_tools_come_first_on_the_path(self, wine_base: Path, calls: _Calls) -> None:
        root = _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'], wait=False)

        path = calls.popen[0]['env']['PATH']

        assert path.startswith(str(root / 'lib' / 'wine' / 'i386-unix'))
        assert path.endswith('/bin:/usr/bin')

    def test_the_rest_of_the_environment_is_inherited(
        self, wine_base: Path, calls: _Calls, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _runner_tree(wine_base)
        monkeypatch.setenv('SOME_SETTING', 'kept')
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'], wait=False)

        assert calls.popen[0]['env']['SOME_SETTING'] == 'kept'

    def test_the_overrides_of_the_caller_are_kept(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'], environment={'WINEDLLOVERRIDES': 'winegstreamer='}, wait=False)

        assert calls.popen[0]['env']['WINEDLLOVERRIDES'] == 'winemenubuilder.exe=;winegstreamer='

    def test_nothing_run_in_a_prefix_builds_start_menu_entries(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'installer.exe'], wait=False)

        assert calls.popen[0]['env']['WINEDLLOVERRIDES'] == 'winemenubuilder.exe='

    def test_the_architecture_is_passed_through(self, wine_base: Path, tmp_path: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', prefix=tmp_path / 'new.wine', arch='win32')

        runner.run_in_prefix([runner.wine, 'hostname'], wait=False)

        assert calls.popen[0]['env']['WINEARCH'] == 'win32'

    def test_output_is_captured_by_default(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'], wait=False)

        assert calls.popen[0]['stdout'] == subprocess.PIPE

    def test_a_command_that_talks_keeps_the_terminal(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'], wait=False, capture_output=False)

        assert calls.popen[0]['stdout'] is None

    def test_it_waits_for_the_wineserver_by_default(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'])

        assert calls.run[0]['cmd'] == [runner.wineserver, '-w']

    def test_and_can_be_told_not_to(self, wine_base: Path, calls: _Calls) -> None:
        _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.run_in_prefix([runner.wine, 'hostname'], wait=False)

        assert calls.run == []

    def test_a_failure_is_logged_rather_than_raised(
        self, wine_base: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        _runner_tree(wine_base)

        monkeypatch.setattr(subprocess, 'Popen', _failing)
        runner = wine.Runner('wine-tkg', 'bottle')

        with caplog.at_level(logging.ERROR, logger=wine.__name__):
            runner.run_in_prefix([runner.wine, 'hostname'], wait=False)

        assert 'exited with 1' in caplog.text

    def test_the_wineserver_is_reached_through_the_runner_path(self, wine_base: Path, calls: _Calls) -> None:
        root = _runner_tree(wine_base)
        runner = wine.Runner('wine-tkg', 'bottle')

        runner.wait()

        assert calls.run[0]['env']['PATH'].startswith(str(root / 'lib' / 'wine' / 'i386-unix'))
        assert calls.run[0]['env']['WINEPREFIX'] == str(runner.prefix_dir)


class TestCreateOrUpdateBottle:
    @staticmethod
    def _built(path: Path) -> Path:
        prefix = _prefix(path)
        (prefix / 'system.reg').write_text('WINE REGISTRY Version 2\n')
        return prefix

    @staticmethod
    def _wine_inf(root: Path) -> Path:
        return _touch(root / 'share' / 'wine' / 'wine.inf')

    def test_a_new_prefix_is_booted_and_stamped(
        self, wine_base: Path, tmp_path: Path, calls: _Calls, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _runner_tree(wine_base)
        inf = self._wine_inf(root)
        prefix = tmp_path / 'Game.wine'

        runner = wine.Runner('wine-tkg', prefix=prefix)
        # wineboot is what writes it, and nothing here really runs wine
        monkeypatch.setattr(runner, 'run_in_prefix', _bootstrapping(prefix))

        runner.create_or_update_prefix()

        assert (prefix / '.update-timestamp').read_text().strip() == str(int(inf.stat().st_mtime))

    def test_a_prefix_of_the_same_runner_is_left_alone(
        self, wine_base: Path, tmp_path: Path, calls: _Calls, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _runner_tree(wine_base)
        inf = self._wine_inf(root)
        prefix = self._built(tmp_path / 'Game.wine')
        (prefix / '.update-timestamp').write_text(f'{int(inf.stat().st_mtime)}\n')

        runner = wine.Runner('wine-tkg', prefix=prefix)
        ran: list[Any] = []
        monkeypatch.setattr(runner, 'run_in_prefix', _recording(ran))

        runner.create_or_update_prefix()

        assert ran == []

    def test_a_prefix_of_another_runner_is_booted_again(
        self, wine_base: Path, tmp_path: Path, calls: _Calls, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _runner_tree(wine_base)
        inf = self._wine_inf(root)
        prefix = self._built(tmp_path / 'Game.wine')
        (prefix / '.update-timestamp').write_text('1\n')

        runner = wine.Runner('wine-tkg', prefix=prefix)
        ran: list[Any] = []
        monkeypatch.setattr(runner, 'run_in_prefix', _recording(ran))

        runner.create_or_update_prefix()

        assert ran == [[runner.wine, 'wineboot', '-u']]
        assert (prefix / '.update-timestamp').read_text().strip() == str(int(inf.stat().st_mtime))

    def test_the_links_of_the_runner_that_is_gone_are_dropped(
        self, wine_base: Path, tmp_path: Path, calls: _Calls, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _runner_tree(wine_base)
        self._wine_inf(root)
        prefix = self._built(tmp_path / 'Game.wine')
        system32 = prefix / 'drive_c' / 'windows' / 'system32'
        system32.mkdir(parents=True)
        stale = system32 / 'd3d11.dll'
        stale.symlink_to(tmp_path / 'gone' / 'd3d11.dll')
        theirs = system32 / 'game.dll'
        theirs.write_text('')

        runner = wine.Runner('wine-tkg', prefix=prefix)
        monkeypatch.setattr(runner, 'run_in_prefix', _nothing)

        runner.create_or_update_prefix()

        assert not stale.is_symlink()
        assert theirs.exists()

    def test_a_prefix_keeping_wine_mono_out_says_so_to_wineboot(
        self, wine_base: Path, tmp_path: Path, calls: _Calls, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _runner_tree(wine_base)
        self._wine_inf(root)
        prefix = self._built(tmp_path / 'Game.wine')
        (prefix / 'user.reg').write_text('[Software\\Wine\\DllOverrides]\n"*mscoree"="native"\n')

        runner = wine.Runner('wine-tkg', prefix=prefix)
        environments: list[Any] = []
        monkeypatch.setattr(runner, 'run_in_prefix', _recording_environment(environments))

        runner.create_or_update_prefix()

        assert environments == [{'WINEDLLOVERRIDES': 'mscoree,mshtml='}]

    def test_a_runner_without_a_wine_inf_says_nothing_to_compare(
        self, wine_base: Path, tmp_path: Path, calls: _Calls, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _runner_tree(wine_base)
        prefix = self._built(tmp_path / 'Game.wine')

        runner = wine.Runner('wine-tkg', prefix=prefix)
        ran: list[Any] = []
        monkeypatch.setattr(runner, 'run_in_prefix', _recording(ran))

        runner.create_or_update_prefix()

        assert ran == []
        assert not (prefix / '.update-timestamp').exists()


class TestForcesHidraw:
    def test_a_winebus_that_reads_hidraw_itself_is_recognised(self, wine_base: Path, tmp_path: Path) -> None:
        root = _runner_tree(wine_base)
        winebus = root / 'lib' / 'wine' / 'x86_64-unix' / 'winebus.so'
        winebus.write_bytes(b'\x7fELF...hidraw handles native reports...')

        assert wine.Runner('wine-tkg', prefix=_prefix(tmp_path / 'Game.wine')).forces_hidraw is True

    def test_any_other_winebus_does_not(self, wine_base: Path, tmp_path: Path) -> None:
        root = _runner_tree(wine_base)
        (root / 'lib' / 'wine' / 'x86_64-unix' / 'winebus.so').write_bytes(b'\x7fELF')

        assert wine.Runner('wine-tkg', prefix=_prefix(tmp_path / 'Game.wine')).forces_hidraw is False

    def test_a_runner_without_one_does_not(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        assert wine.Runner('wine-tkg', prefix=_prefix(tmp_path / 'Game.wine')).forces_hidraw is False


class TestRunnerConstructors:
    def test_default_uses_the_default_runner(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        runner = wine.Runner.default('model2')

        assert runner.runner_name == 'wine-tkg'
        assert runner.prefix_dir == tmp_path / 'bottles' / 'model2'

    def test_from_prefix_without_a_name_uses_the_default_runner(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        runner = wine.Runner.from_prefix(None, tmp_path / 'Game.wine')

        assert runner.runner_name == 'wine-tkg'
        assert runner.prefix_dir == tmp_path / 'Game.wine'

    def test_from_prefix_carries_the_architecture(self, wine_base: Path, tmp_path: Path) -> None:
        _runner_tree(wine_base)

        runner = wine.Runner.from_prefix('wine-tkg', tmp_path / 'Game.wine', arch='win32')

        assert runner.arch == 'win32'


def test_the_module_reads_nothing_outside_the_temporary_tree(wine_base: Path) -> None:
    _runner_tree(wine_base)

    runner = wine.Runner('wine-tkg', 'bottle')

    assert str(runner.wine).startswith(str(wine_base))
    assert not str(runner.prefix_dir).startswith(str(Path(os.sep, 'userdata')))
