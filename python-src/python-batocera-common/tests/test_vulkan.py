from __future__ import annotations

from subprocess import CalledProcessError
from typing import TYPE_CHECKING

import pytest

from batocera_common import vulkan

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    import pytest_mock
    from pyfakefs.fake_filesystem import FakeFilesystem

SUMMARY_OUTPUT = """\
==========
VULKANINFO
==========

Vulkan Instance Version: 1.4.341

Devices:
========
GPU0:
 apiVersion = 1.4.328
 driverVersion = 25.3.5
 vendorID = 0x1002
 deviceID = 0x744c
 deviceType = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
 deviceName = AMD Radeon RX 7900 XTX (RADV NAVI31)
 driverID = DRIVER_ID_MESA_RADV
 driverName = radv
 driverInfo = Mesa 25.3.5-arch1.1
 conformanceVersion = 1.4.0.0
 deviceUUID = 00000000-2d00-0000-0000-000000000000
 driverUUID = 414d442d-4d45-5341-2d44-525600000000
GPU1:
 apiVersion = 1.4.328
 driverVersion = 25.3.5
 vendorID = 0x10005
 deviceID = 0x0000
 deviceType = PHYSICAL_DEVICE_TYPE_CPU
 deviceName = llvmpipe (LLVM 21.1.6, 256 bits)
 driverID = DRIVER_ID_MESA_LLVMPIPE
 driverName = llvmpipe
 driverInfo = Mesa 25.3.5-arch1.1 (LLVM 21.1.6)
 conformanceVersion = 1.3.1.1
 deviceUUID = 6d657361-3235-2e33-2e35-2d6172636800
 driverUUID = 6c6c766d-7069-7065-5555-494400000000
"""

HYBRID_OUTPUT = """\
Devices:
========
GPU0:
 apiVersion = 1.3.280
 deviceType = PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU
 deviceName = Intel(R) UHD Graphics 630
 deviceUUID = 11111111-1111-1111-1111-111111111111
GPU1:
 apiVersion = 1.4.328
 deviceType = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
 deviceName = AMD Radeon RX 7900 XTX (RADV NAVI31)
 deviceUUID = 00000000-2d00-0000-0000-000000000000
"""

FULL_GPU0_OUTPUT = """\
GPU0:
========
\tVkPhysicalDeviceProperties:
\t---------------------------
\t\tapiVersion         = 1.4.328 (4210991)
\t\tdriverVersion      = 25.3.5
\t\tvendorID           = 0x1002
\t\tdeviceID           = 0x744c
\t\tdeviceType         = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
\t\tdeviceName         = AMD Radeon RX 7900 XTX (RADV NAVI31)

\tDevice Extensions: count = 4
\t--------------------------
\t\tVK_KHR_swapchain                              : extension revision 70
\t\tVK_KHR_video_encode_av1                       : extension revision 1
\t\tVK_KHR_video_encode_queue                     : extension revision 8
\t\tVK_KHR_video_queue                            : extension revision 8
GPU1:
========
\tVkPhysicalDeviceProperties:
\t---------------------------
\t\tdeviceType         = PHYSICAL_DEVICE_TYPE_CPU
\t\tdeviceName         = llvmpipe (LLVM 21.1.6, 256 bits)
"""

INTEGRATED_GPU = vulkan.VulkanGPU(
    index=0,
    name='Intel(R) UHD Graphics 630',
    device_type='PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU',
    uuid='11111111-1111-1111-1111-111111111111',
    api_version='1.3.280',
    extensions=frozenset(),
)

DISCRETE_GPU = vulkan.VulkanGPU(
    index=1,
    name='AMD Radeon RX 7900 XTX (RADV NAVI31)',
    device_type='PHYSICAL_DEVICE_TYPE_DISCRETE_GPU',
    uuid='00000000-2d00-0000-0000-000000000000',
    api_version='1.4.328',
    extensions=frozenset(),
)


@pytest.fixture(autouse=True)
def reset_vulkan_info_cache() -> None:
    vulkan._get_cached_vulkan_info.cache_clear()


@pytest.fixture
def mock_vulkaninfo(request: pytest.FixtureRequest, mocker: pytest_mock.MockFixture) -> AsyncMock:
    from batocera_common.asyncio import AsyncCompletedProcess

    if request.param == 'summary':
        output = SUMMARY_OUTPUT
    elif request.param == 'hybrid':
        output = HYBRID_OUTPUT
    elif request.param == 'full':
        output = FULL_GPU0_OUTPUT
    elif request.param == 'none':
        output = ''
    elif request.param == 'error':
        output = None
    else:
        raise ValueError('unknown param')

    if output is not None:
        return_value = AsyncCompletedProcess(returncode=0, stdout=output, stderr='')
        side_effect = None
    else:
        return_value = None
        side_effect = CalledProcessError(1, ['/usr/bin/vulkaninfo'])

    return mocker.patch.object(
        vulkan,
        'run',
        return_value=return_value,
        side_effect=side_effect,
        new_callable=mocker.AsyncMock,
    )


async def test_get_vulkan_info_no_binary() -> None:
    info = await vulkan.get_vulkan_info()

    assert info is None


@pytest.mark.parametrize('mock_vulkaninfo', ['error'], indirect=True)
@pytest.mark.usefixtures('mock_vulkaninfo')
async def test_get_vulkan_info_run_exception(fs: FakeFilesystem) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]

    info = await vulkan.get_vulkan_info()

    assert info is None


@pytest.mark.parametrize('mock_vulkaninfo', ['none'], indirect=True)
@pytest.mark.usefixtures('mock_vulkaninfo')
async def test_get_vulkan_info_no_gpus(fs: FakeFilesystem) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]

    info = await vulkan.get_vulkan_info()

    assert info is None


@pytest.mark.parametrize('mock_vulkaninfo', ['summary'], indirect=True)
@pytest.mark.usefixtures('mock_vulkaninfo')
async def test_get_vulkan_info_summary(fs: FakeFilesystem) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]

    info = await vulkan.get_vulkan_info()

    assert info is not None
    assert len(info.gpus) == 2
    assert info.devices == [
        'AMD Radeon RX 7900 XTX (RADV NAVI31)',
        'llvmpipe (LLVM 21.1.6, 256 bits)',
    ]
    assert info.default_gpu is not None
    assert info.default_gpu.name == 'AMD Radeon RX 7900 XTX (RADV NAVI31)'
    assert info.discrete_gpu is not None
    assert info.discrete_gpu.index == 0
    assert info.discrete_gpu.uuid == '00000000-2d00-0000-0000-000000000000'
    assert info.discrete_gpu.api_version == '1.4.328'
    assert info.active_discrete_gpu == info.discrete_gpu
    assert info.active_gpu == info.discrete_gpu
    assert info.version == '1.4.328'


@pytest.mark.parametrize('mock_vulkaninfo', ['full'], indirect=True)
@pytest.mark.usefixtures('mock_vulkaninfo')
async def test_get_vulkan_info_device_extensions(fs: FakeFilesystem) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]

    info = await vulkan.get_vulkan_info()

    assert info is not None
    assert info.discrete_gpu is not None
    assert 'VK_KHR_video_queue' in info.discrete_gpu.extensions
    assert 'VK_KHR_video_encode_queue' in info.discrete_gpu.extensions
    assert 'VK_KHR_video_encode_av1' in info.discrete_gpu.extensions
    assert info.discrete_gpu.api_version == '1.4.328'
    assert info.encoding_codecs == ['av1_vulkan']


@pytest.mark.parametrize('mock_vulkaninfo', ['summary'], indirect=True)
async def test_get_vulkan_info_preserves_display(
    fs: FakeFilesystem,
    monkeypatch: pytest.MonkeyPatch,
    mock_vulkaninfo: AsyncMock,
) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]
    monkeypatch.setenv('DISPLAY', ':1')
    monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)

    await vulkan.get_vulkan_info()

    assert mock_vulkaninfo.await_count == 1
    assert mock_vulkaninfo.await_args_list[0].kwargs['env'].get('DISPLAY') == ':1'


@pytest.mark.parametrize('mock_vulkaninfo', ['summary'], indirect=True)
async def test_get_vulkan_info_preserves_wayland_display(
    fs: FakeFilesystem,
    monkeypatch: pytest.MonkeyPatch,
    mock_vulkaninfo: AsyncMock,
) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]
    monkeypatch.setenv('WAYLAND_DISPLAY', 'wayland-0')
    monkeypatch.delenv('DISPLAY', raising=False)

    await vulkan.get_vulkan_info()

    assert mock_vulkaninfo.await_count == 1
    env = mock_vulkaninfo.await_args_list[0].kwargs['env']
    assert env.get('WAYLAND_DISPLAY') == 'wayland-0'
    assert 'DISPLAY' not in env


@pytest.mark.parametrize('mock_vulkaninfo', ['summary'], indirect=True)
async def test_get_vulkan_info_discovers_display_from_x_socket(
    fs: FakeFilesystem,
    monkeypatch: pytest.MonkeyPatch,
    mock_vulkaninfo: AsyncMock,
) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]
    fs.create_file('/tmp/.X11-unix/X0')  # pyright: ignore[reportUnknownMemberType]
    monkeypatch.delenv('DISPLAY', raising=False)
    monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)

    await vulkan.get_vulkan_info()

    assert mock_vulkaninfo.await_count == 1
    env = mock_vulkaninfo.await_args_list[0].kwargs['env']
    assert env['DISPLAY'] == ':0'


@pytest.mark.parametrize('mock_vulkaninfo', ['summary'], indirect=True)
async def test_get_vulkan_info_uses_lowest_x_socket(
    fs: FakeFilesystem,
    monkeypatch: pytest.MonkeyPatch,
    mock_vulkaninfo: AsyncMock,
) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]
    fs.create_file('/tmp/.X11-unix/X1')  # pyright: ignore[reportUnknownMemberType]
    fs.create_file('/tmp/.X11-unix/X0')  # pyright: ignore[reportUnknownMemberType]
    monkeypatch.delenv('DISPLAY', raising=False)
    monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)

    await vulkan.get_vulkan_info()

    assert mock_vulkaninfo.await_count == 1
    env = mock_vulkaninfo.await_args_list[0].kwargs['env']
    assert env['DISPLAY'] == ':0'


@pytest.mark.parametrize('mock_vulkaninfo', ['summary'], indirect=True)
async def test_get_vulkan_info_no_display_without_x_sockets(
    fs: FakeFilesystem,
    monkeypatch: pytest.MonkeyPatch,
    mock_vulkaninfo: AsyncMock,
) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]
    monkeypatch.delenv('DISPLAY', raising=False)
    monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)

    await vulkan.get_vulkan_info()

    assert mock_vulkaninfo.await_count == 1
    env = mock_vulkaninfo.await_args_list[0].kwargs['env']
    assert 'DISPLAY' not in env


def test_vulkan_info_encoding_codecs() -> None:
    gpu = vulkan.VulkanGPU(
        index=0,
        name='AMD Radeon RX 7900 XTX (RADV NAVI31)',
        device_type='PHYSICAL_DEVICE_TYPE_DISCRETE_GPU',
        uuid=None,
        api_version='1.4.328',
        extensions=frozenset(
            {
                'VK_KHR_video_queue',
                'VK_KHR_video_encode_queue',
                'VK_KHR_video_encode_av1',
            }
        ),
    )
    info = vulkan.VulkanInfo(gpus=(gpu,))

    assert info.encoding_codecs == ['av1_vulkan']


def test_vulkan_info_active_discrete_respects_radeon_prime(fs: FakeFilesystem) -> None:
    fs.create_file(  # pyright: ignore[reportUnknownMemberType]
        '/boot/batocera-boot.conf', contents='radeon-prime=false\n'
    )

    info = vulkan.VulkanInfo(gpus=(INTEGRATED_GPU, DISCRETE_GPU))

    assert info.discrete_gpu == DISCRETE_GPU
    assert info.active_discrete_gpu is None
    assert info.active_gpu == INTEGRATED_GPU
    assert info.version == '1.3.280'


def test_vulkan_info_discrete_gpu_without_active_discrete(fs: FakeFilesystem) -> None:
    fs.create_file(  # pyright: ignore[reportUnknownMemberType]
        '/boot/batocera-boot.conf', contents='radeon-prime=false\n'
    )

    info = vulkan.VulkanInfo(gpus=(INTEGRATED_GPU, DISCRETE_GPU))

    assert info.discrete_gpu is not None
    assert info.discrete_gpu.name == 'AMD Radeon RX 7900 XTX (RADV NAVI31)'
    assert info.discrete_gpu.index == 1
    assert info.discrete_gpu.uuid == '00000000-2d00-0000-0000-000000000000'


@pytest.mark.parametrize('mock_vulkaninfo', ['summary'], indirect=True)
@pytest.mark.usefixtures('mock_vulkaninfo')
def test_sync_helpers(fs: FakeFilesystem) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]

    assert vulkan.is_available() is True
    assert vulkan.has_discrete_gpu() is True
    assert vulkan.get_discrete_gpu_index() == '0'
    assert vulkan.get_discrete_gpu_name() == 'AMD Radeon RX 7900 XTX (RADV NAVI31)'
    assert vulkan.get_default_gpu_name() == 'AMD Radeon RX 7900 XTX (RADV NAVI31)'
    assert vulkan.get_discrete_gpu_uuid() == '00000000-2d00-0000-0000-000000000000'
    assert vulkan.get_version() == '1.4.328'


@pytest.mark.parametrize('mock_vulkaninfo', ['hybrid'], indirect=True)
@pytest.mark.usefixtures('mock_vulkaninfo')
def test_sync_helpers_respect_radeon_prime(fs: FakeFilesystem) -> None:
    fs.create_file('/usr/bin/vulkaninfo')  # pyright: ignore[reportUnknownMemberType]
    fs.create_file(  # pyright: ignore[reportUnknownMemberType]
        '/boot/batocera-boot.conf', contents='radeon-prime=false\n'
    )

    assert vulkan.is_available() is True
    assert vulkan.has_discrete_gpu() is False
    assert vulkan.get_discrete_gpu_name() == 'AMD Radeon RX 7900 XTX (RADV NAVI31)'
    assert vulkan.get_discrete_gpu_index() == '1'
    assert vulkan.get_discrete_gpu_uuid() == '00000000-2d00-0000-0000-000000000000'
    assert vulkan.get_default_gpu_name() == 'Intel(R) UHD Graphics 630'
    assert vulkan.get_version() == '1.3.280'
