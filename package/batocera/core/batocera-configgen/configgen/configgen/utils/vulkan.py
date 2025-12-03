from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Final

_logger: Final = logging.getLogger(__name__)

_BATOCERA_VULKAN: Final = Path('/usr/bin/batocera-vulkan')


def is_available() -> bool:
    try:
        return subprocess.check_output([_BATOCERA_VULKAN, 'hasVulkan'], text=True).strip() == 'true'
    except subprocess.CalledProcessError:
        _logger.exception('Error checking for Vulkan driver')

    return False


def has_discrete_gpu() -> bool:
    try:
        return subprocess.check_output([_BATOCERA_VULKAN, 'hasDiscrete'], text=True).strip() == 'true'
    except subprocess.CalledProcessError:
        _logger.exception('Error checking for discrete GPU.')

    return False


def get_discrete_gpu_index() -> str | None:
    try:
        return subprocess.check_output([_BATOCERA_VULKAN, 'discreteIndex'], text=True).strip() or None
    except subprocess.CalledProcessError:
        _logger.exception('Error getting discrete GPU index')

    return None


def get_discrete_gpu_name() -> str | None:
    try:
        return subprocess.check_output([_BATOCERA_VULKAN, 'discreteName'], text=True).strip() or None
    except subprocess.CalledProcessError:
        _logger.exception('Error getting discrete GPU Name')

    return None


def get_default_gpu_name() -> str | None:
    try:
        return subprocess.check_output([_BATOCERA_VULKAN, 'defaultName'], text=True).strip() or None
    except subprocess.CalledProcessError:
        _logger.exception('Error getting default GPU Name')

    return None


def get_discrete_gpu_uuid() -> str | None:
    try:
        return subprocess.check_output([_BATOCERA_VULKAN, 'discreteUUID'], text=True).strip() or None
    except subprocess.CalledProcessError:
        _logger.exception('Error getting discrete GPU UUID')

    return None


def get_version() -> str:
    try:
        return subprocess.check_output([_BATOCERA_VULKAN, 'vulkanVersion'], text=True).strip()
    except subprocess.CalledProcessError:
        _logger.exception('Error checking for Vulkan version.')

    return ''
