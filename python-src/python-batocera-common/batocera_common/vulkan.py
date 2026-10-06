from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Final

from .asyncio import run
from .dataclasses import cached_dataclass, cached_property
from .key_value_config import KeyValueConfig

_logger: Final = logging.getLogger(__name__)

_BATOCERA_BOOT_CONF: Final = Path('/boot/batocera-boot.conf')
_VULKAN_INFO_BIN: Final = Path('/usr/bin/vulkaninfo')

_GPU_HEADER_RE: Final = re.compile(r'^GPU(\d+):', re.MULTILINE)
_KEY_VALUE_RE: Final = re.compile(r'^\s*(?P<key>[A-Za-z0-9]+)\s*=\s*(?P<value>.+?)\s*$', re.MULTILINE)
_DEVICE_EXTENSIONS_RE: Final = re.compile(
    r'^\s*Device Extensions:.*?(?=^\s*(?:GPU\d+:|Device Groups:)|\Z)',
    re.MULTILINE | re.DOTALL,
)
_EXTENSION_NAME_RE: Final = re.compile(r'^\s*(VK_[A-Za-z0-9_]+)\s+:', re.MULTILINE)

_VIDEO_QUEUE_EXTENSIONS: Final = frozenset({'VK_KHR_video_queue', 'VK_KHR_video_encode_queue'})
_ENCODING_EXTENSIONS: Final = {
    'VK_KHR_video_encode_h264': 'h264_vulkan',
    'VK_KHR_video_encode_h265': 'hevc_vulkan',
    'VK_KHR_video_encode_av1': 'av1_vulkan',
}


@cached_dataclass(frozen=True)
class VulkanGPU:
    index: int
    name: str
    device_type: str
    uuid: str | None
    api_version: str
    extensions: frozenset[str]

    @cached_property
    def is_discrete(self) -> bool:
        return self.device_type == 'PHYSICAL_DEVICE_TYPE_DISCRETE_GPU'


@cached_dataclass(frozen=True)
class VulkanInfo:
    gpus: tuple[VulkanGPU, ...]

    @cached_property
    def devices(self) -> list[str]:
        return [gpu.name for gpu in self.gpus]

    @cached_property
    def default_gpu(self) -> VulkanGPU | None:
        return self.gpus[0] if self.gpus else None

    @cached_property
    def discrete_gpu(self) -> VulkanGPU | None:
        return next((gpu for gpu in self.gpus if gpu.is_discrete), None)

    @cached_property
    def active_discrete_gpu(self) -> VulkanGPU | None:
        if self.discrete_gpu is not None and not _is_radeon_prime_disabled():
            return self.discrete_gpu

        return None

    @cached_property
    def active_gpu(self) -> VulkanGPU | None:
        return self.active_discrete_gpu or self.default_gpu

    @cached_property
    def version(self) -> str | None:
        if self.active_gpu is not None:
            return self.active_gpu.api_version

        return None

    @cached_property
    def encoding_codecs(self) -> list[str]:
        gpu = self.active_gpu
        if gpu is None or not _VIDEO_QUEUE_EXTENSIONS.issubset(gpu.extensions):
            return []

        return [codec for extension, codec in _ENCODING_EXTENSIONS.items() if extension in gpu.extensions]


def _parse_api_version(raw_value: str) -> str:
    value = raw_value.strip()
    if '(' in value:
        value = value[: value.index('(')].strip()

    return value


def _parse_device_extensions(block: str) -> frozenset[str]:
    match = _DEVICE_EXTENSIONS_RE.search(block)
    if match is None:
        return frozenset()

    return frozenset(_EXTENSION_NAME_RE.findall(match.group(0)))


def _parse_gpu_block(index: int, block: str) -> VulkanGPU:
    properties = {
        match.group('key'): match.group('value').strip()
        for match in _KEY_VALUE_RE.finditer(block)
        if match.group('key') in {'deviceName', 'deviceType', 'deviceUUID', 'apiVersion'}
    }

    return VulkanGPU(
        index=index,
        name=properties.get('deviceName', ''),
        device_type=properties.get('deviceType', ''),
        uuid=properties.get('deviceUUID'),
        api_version=_parse_api_version(properties.get('apiVersion', '')),
        extensions=_parse_device_extensions(block),
    )


def _parse_vulkaninfo(text: str) -> VulkanInfo | None:
    matches = list(_GPU_HEADER_RE.finditer(text))
    gpus: list[VulkanGPU] = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        gpus.append(_parse_gpu_block(int(match.group(1)), text[start:end]))

    if not gpus:
        return None

    return VulkanInfo(gpus=tuple(gpus))


def _is_radeon_prime_disabled() -> bool:
    if not _BATOCERA_BOOT_CONF.is_file():
        return False

    value = KeyValueConfig(_BATOCERA_BOOT_CONF).get('radeon-prime')

    return value is not None and value.strip() == 'false'


def _vulkan_env() -> dict[str, str]:
    env = dict(os.environ)

    if not env.get('WAYLAND_DISPLAY') and not env.get('DISPLAY'):
        x_sockets = sorted(Path('/tmp/.X11-unix').glob('X*'))
        if x_sockets:
            env['DISPLAY'] = f':{x_sockets[0].name[1:]}'

    return env


async def get_vulkan_info() -> VulkanInfo | None:
    if not _VULKAN_INFO_BIN.exists():
        _logger.warning('vulkaninfo binary not found.')
        return None

    try:
        proc = await run(_VULKAN_INFO_BIN, check=True, text=True, env=_vulkan_env())
    except Exception:
        _logger.exception('Error running vulkaninfo')
        return None

    return _parse_vulkaninfo(proc.stdout)
