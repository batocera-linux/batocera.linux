from __future__ import annotations

from typing import TYPE_CHECKING

import evdev
from evdev import ecodes

from batocera_launch.devices.controller import Controller

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

_STICKS = (ecodes.ABS_X, ecodes.ABS_Y, ecodes.ABS_Z, ecodes.ABS_RX, ecodes.ABS_RY, ecodes.ABS_RZ)
_HAT = (ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y)


def _controller() -> Controller:
    return Controller(
        name='Test Pad',
        type='joystick',
        guid='050000005e0400008e02000030110000',
        player_number=1,
        index=0,
        real_name='Test Pad',
        device_path='/dev/input/event3',
        button_count=11,
        hat_count=1,
        axis_count=7,
    )


def _mock_device(mocker: MockerFixture, axes: dict[int, tuple[int, int]], /) -> None:
    device = mocker.MagicMock()
    device.capabilities.return_value = {
        ecodes.EV_ABS: [(code, evdev.AbsInfo(0, low, high, 0, 0, 0)) for code, (low, high) in axes.items()]
    }
    mocker.patch('evdev.InputDevice', return_value=device)


def test_hats_are_numbered_before_a_later_axis(mocker: MockerFixture) -> None:
    _mock_device(mocker, dict.fromkeys((*_STICKS, *_HAT, ecodes.ABS_PROFILE), (-1, 1)))

    numbers = _controller().get_evdev_axis_numbers()

    assert numbers is not None
    assert numbers[ecodes.ABS_HAT0X] == 6
    assert numbers[ecodes.ABS_HAT0Y] == 7
    assert numbers[ecodes.ABS_PROFILE] == 8


def test_codes_from_abs_misc_are_left_out(mocker: MockerFixture) -> None:
    _mock_device(mocker, dict.fromkeys((*_STICKS, *_HAT, ecodes.ABS_MISC), (-1, 1)))

    assert _controller().get_evdev_axis_numbers() == {code: n for n, code in enumerate((*_STICKS, *_HAT))}


def test_skip_flat_drops_axes_without_a_range(mocker: MockerFixture) -> None:
    _mock_device(mocker, {ecodes.ABS_X: (-1, 1), ecodes.ABS_Y: (0, 0), ecodes.ABS_HAT0X: (-1, 1)})

    assert _controller().get_evdev_axis_numbers() == {ecodes.ABS_X: 0, ecodes.ABS_Y: 1, ecodes.ABS_HAT0X: 2}
    assert _controller().get_evdev_axis_numbers(skip_flat=True) == {ecodes.ABS_X: 0, ecodes.ABS_HAT0X: 1}


def test_missing_device_returns_none(mocker: MockerFixture) -> None:
    mocker.patch('evdev.InputDevice', side_effect=OSError)

    assert _controller().get_evdev_axis_numbers() is None
