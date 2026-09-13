from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from batocera_common.asyncio import AsyncCompletedProcess
from batocera_launch.command import Command
from batocera_launch.config.config import Config
from batocera_launch.exceptions import BatoceraException
from batocera_launch.gamescope import add_gamescope_arguments, is_gbm_supported
from batocera_launch.types import Resolution

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

pytestmark = [pytest.mark.usefixtures('fs'), pytest.mark.asyncio]

_EGLINFO = Path('/usr/bin/eglinfo')
_GBM_OUTPUT = 'EGL client extensions string:\n    EGL_EXT_platform_base EGL_KHR_platform_gbm\n'
_NO_GBM_OUTPUT = 'EGL client extensions string:\n    EGL_EXT_platform_base EGL_KHR_platform_x11\n'

_ROM_ARGS = ['/usr/bin/retroarch', '-L', 'core.so', '/userdata/roms/snes/game.zip']
_RESOLUTION = Resolution(width=1920, height=1080)


@pytest.fixture(autouse=True)
def no_wayland_display(monkeypatch: pytest.MonkeyPatch) -> None:
    # the machine running the tests may well be under wayland itself
    monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)


@pytest.fixture
def eglinfo(fs: FakeFilesystem) -> Path:
    _EGLINFO.parent.mkdir(parents=True, exist_ok=True)
    _EGLINFO.touch()
    return _EGLINFO


def _mock_run(mocker: MockerFixture, stdout: str) -> Any:
    return mocker.patch(
        'batocera_launch.gamescope.run',
        return_value=AsyncCompletedProcess(returncode=0, stdout=stdout, stderr=''),
    )


@pytest.fixture
def gbm(eglinfo: Path, mocker: MockerFixture) -> Any:
    return _mock_run(mocker, _GBM_OUTPUT)


def _command() -> Command:
    return Command(args=list(_ROM_ARGS))


async def _configure(config: dict[str, Any], /, *, resolution: Resolution = _RESOLUTION) -> Command:
    command = _command()
    await add_gamescope_arguments(command, Config(config), resolution)
    return command


def _gamescope_args(command: Command, /) -> list[str]:
    args = [str(arg) for arg in command.args]
    separator = args.index('--')

    assert args[separator + 1 :] == _ROM_ARGS, 'the wrapped command must be left untouched'

    return args[:separator]


class TestIsGbmSupported:
    async def test_returns_false_when_eglinfo_is_missing(self, mocker: MockerFixture) -> None:
        run = _mock_run(mocker, _GBM_OUTPUT)

        assert await is_gbm_supported() is False
        run.assert_not_called()

    async def test_returns_true_when_the_gbm_extension_is_advertised(self, gbm: Any) -> None:
        assert await is_gbm_supported() is True
        gbm.assert_called_once_with(_EGLINFO, text=True)

    async def test_returns_false_when_the_gbm_extension_is_absent(self, eglinfo: Path, mocker: MockerFixture) -> None:
        _mock_run(mocker, _NO_GBM_OUTPUT)

        assert await is_gbm_supported() is False

    async def test_returns_false_when_eglinfo_fails(
        self, eglinfo: Path, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
    ) -> None:
        mocker.patch('batocera_launch.gamescope.run', side_effect=OSError('boom'))

        assert await is_gbm_supported() is False
        assert 'Failed to run' in caplog.text


class TestAddGamescopeArguments:
    async def test_does_nothing_when_disabled(self, eglinfo: Path, mocker: MockerFixture) -> None:
        run = _mock_run(mocker, _GBM_OUTPUT)

        command = await _configure({})

        assert command.args == _ROM_ARGS
        run.assert_not_called()

    @pytest.mark.parametrize('value', ['0', 'false', 'off'])
    async def test_does_nothing_when_turned_off(self, value: str, gbm: Any) -> None:
        command = await _configure({'gamescope': value})

        assert command.args == _ROM_ARGS

    async def test_raises_when_the_driver_has_no_gbm_support(self, eglinfo: Path, mocker: MockerFixture) -> None:
        _mock_run(mocker, _NO_GBM_OUTPUT)

        with pytest.raises(BatoceraException):
            await _configure({'gamescope': '1'})

    async def test_wraps_the_command_with_the_screen_resolution(self, gbm: Any) -> None:
        command = await _configure({'gamescope': '1'})

        assert [str(arg) for arg in command.args] == [
            '/usr/bin/gamescope',
            '-W',
            '1920',
            '-H',
            '1080',
            '-f',
            '--',
            *_ROM_ARGS,
        ]

    async def test_output_resolution_overrides_the_screen_resolution(self, gbm: Any) -> None:
        command = await _configure({'gamescope': '1', 'gamescope_output_resolution': '3840x2160'})

        assert _gamescope_args(command) == ['/usr/bin/gamescope', '-W', '3840', '-H', '2160', '-f']

    async def test_resolutions_are_stripped(self, gbm: Any) -> None:
        command = await _configure(
            {
                'gamescope': '1',
                'gamescope_output_resolution': ' 3840 x 2160 ',
                'gamescope_nested_resolution': ' 1280 x 720 ',
            }
        )

        assert _gamescope_args(command) == [
            '/usr/bin/gamescope',
            '-W',
            '3840',
            '-H',
            '2160',
            '-w',
            '1280',
            '-h',
            '720',
            '-f',
        ]

    async def test_scaling_and_rate_options(self, gbm: Any) -> None:
        command = await _configure(
            {
                'gamescope': '1',
                'gamescope_nested_refresh': '120',
                'gamescope_framerate_limit': '60',
                'gamescope_scaler': 'integer',
                'gamescope_filter': 'fsr',
                'gamescope_sharpness': '5',
                'gamescope_reshade_effect': 'crt.fx',
            }
        )

        assert _gamescope_args(command) == [
            '/usr/bin/gamescope',
            '-W',
            '1920',
            '-H',
            '1080',
            '-r',
            '120',
            '--framerate-limit',
            '60',
            '-S',
            'integer',
            '-F',
            'fsr',
            '--sharpness',
            '5',
            '-f',
            '--reshade-effect',
            'crt.fx',
        ]

    async def test_hdr_options_are_ignored_when_hdr_is_off(self, gbm: Any) -> None:
        command = await _configure(
            {
                'gamescope': '1',
                'gamescope_sdr_gamut_wideness': '0.5',
                'gamescope_hdr_sdr_content_nits': '400',
                'gamescope_hdr_itm_enabled': '1',
                'gamescope_hdr_itm_sdr_nits': '100',
                'gamescope_hdr_itm_target_nits': '1000',
            }
        )

        assert _gamescope_args(command) == ['/usr/bin/gamescope', '-W', '1920', '-H', '1080', '-f']

    async def test_hdr_options(self, gbm: Any) -> None:
        command = await _configure(
            {
                'gamescope': '1',
                'gamescope_hdr': '1',
                'gamescope_sdr_gamut_wideness': '0.5',
                'gamescope_hdr_sdr_content_nits': '400',
                'gamescope_hdr_itm_enabled': '1',
                'gamescope_hdr_itm_sdr_nits': '100',
                'gamescope_hdr_itm_target_nits': '1000',
            }
        )

        assert _gamescope_args(command) == [
            '/usr/bin/gamescope',
            '-W',
            '1920',
            '-H',
            '1080',
            '--sdr-gamut-wideness',
            '0.5',
            '--hdr-sdr-content-nits',
            '400',
            '--hdr-itm-enabled',
            '--hdr-itm-sdr-nits',
            '100',
            '--hdr-itm-target-nits',
            '1000',
            '-f',
        ]

    async def test_hdr_itm_is_not_enabled_on_its_own(self, gbm: Any) -> None:
        command = await _configure({'gamescope': '1', 'gamescope_hdr': '1'})

        assert '--hdr-itm-enabled' not in _gamescope_args(command)

    async def test_exposes_wayland_under_a_wayland_session(self, gbm: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv('WAYLAND_DISPLAY', 'wayland-0')

        command = await _configure({'gamescope': '1'})

        assert '--expose-wayland' in _gamescope_args(command)

    async def test_does_not_expose_wayland_under_x11(self, gbm: Any) -> None:
        command = await _configure({'gamescope': '1'})

        assert '--expose-wayland' not in _gamescope_args(command)

    async def test_wraps_an_already_wrapped_command(self, gbm: Any) -> None:
        command = _command()
        command.prepend_args('mangohud')

        await add_gamescope_arguments(command, Config({'gamescope': '1'}), _RESOLUTION)

        args = [str(arg) for arg in command.args]

        assert args[0] == '/usr/bin/gamescope'
        assert args[args.index('--') + 1 :] == ['mangohud', *_ROM_ARGS]
