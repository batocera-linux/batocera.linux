from __future__ import annotations

import pytest

from batocera_launch.devices.video import _parse_mode, find_mode

# What `batocera-resolution listModes` prints on the labwc backend (millihertz)
_LABWC_MODES = [
    'max-1920x1080',
    'max-640x480',
    '3840x2160.60000',
    '3840x2160.59940',
    '1920x1080.120000',
    '1920x1080.119880',
    '1920x1080.60000',
    '1920x1080.59940',
    '1920x1080.23976',
    '1280x720.60000',
]

# ...and on the Xorg backend (hertz)
_XORG_MODES = [
    'max-1920x1080',
    '1920x1080.60.00',
    '1920x1080.59.94',
    '1280x720.60.00',
]


@pytest.mark.parametrize(
    ('mode', 'expected'),
    [
        ('1920x1080', ('1920x1080', None)),
        ('1920x1080.60000', ('1920x1080', 60000)),
        ('1920x1080.60.00', ('1920x1080', 60000)),
        ('1920x1080.60', ('1920x1080', 60000)),
        ('3840x2160.120.00', ('3840x2160', 120000)),
        ('1920x1080.59.94', ('1920x1080', 59940)),
        ('1920x1080.23976', ('1920x1080', 23976)),
        ('max-1920x1080', None),
        ('default', None),
        ('', None),
    ],
)
def test_parse_mode(mode: str, expected: tuple[str, int | None] | None) -> None:
    assert _parse_mode(mode) == expected


@pytest.mark.parametrize(
    ('requested', 'expected'),
    [
        # exact spelling
        ('1920x1080.60000', '1920x1080.60000'),
        ('1920x1080.120000', '1920x1080.120000'),
        # Xorg-style strings left in an existing config
        ('1920x1080.60.00', '1920x1080.60000'),
        ('1920x1080.60', '1920x1080.60000'),
        ('1920x1080.59.94', '1920x1080.59940'),
        # truncated mHz written by older listings
        ('1920x1080.59939', '1920x1080.59940'),
        ('1920x1080.119879', '1920x1080.119880'),
        # not offered by the display
        ('3840x2160.120.00', None),
        ('1920x1080.75000', None),
        ('1024x768.60.00', None),
        # a resolution without a refresh is only valid as an exact listing
        ('1920x1080', None),
    ],
)
def test_find_mode_labwc(requested: str, expected: str | None) -> None:
    assert find_mode(requested, _LABWC_MODES) == expected


@pytest.mark.parametrize(
    ('requested', 'expected'),
    [
        ('1920x1080.60.00', '1920x1080.60.00'),
        # labwc-style strings in an Xorg config
        ('1920x1080.60000', '1920x1080.60.00'),
        ('1920x1080.59940', '1920x1080.59.94'),
        ('1920x1080.120000', None),
    ],
)
def test_find_mode_xorg(requested: str, expected: str | None) -> None:
    assert find_mode(requested, _XORG_MODES) == expected


def test_find_mode_prefers_exact_match() -> None:
    assert find_mode('1920x1080.60000', ['1920x1080.60001', '1920x1080.60000']) == '1920x1080.60000'


def test_find_mode_does_not_cross_resolutions() -> None:
    assert find_mode('1280x720.60000', ['1920x1080.60000']) is None
