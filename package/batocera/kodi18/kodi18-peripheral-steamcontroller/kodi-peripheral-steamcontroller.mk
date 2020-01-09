################################################################################
#
# kodi-peripheral-steamcontroller
#
################################################################################

KODI18_PERIPHERAL_STEAMCONTROLLER_VERSION = 0347e66dc8464184d636aea2cfe10491d6fcda96
KODI18_PERIPHERAL_STEAMCONTROLLER_SITE = $(call github,kodi-game,peripheral.steamcontroller,$(KODI18_PERIPHERAL_STEAMCONTROLLER_VERSION))
KODI18_PERIPHERAL_STEAMCONTROLLER_LICENSE = GPL-2.0+
KODI18_PERIPHERAL_STEAMCONTROLLER_LICENSE_FILES = src/addon.cpp
KODI18_PERIPHERAL_STEAMCONTROLLER_DEPENDENCIES = kodi18-platform libusb

$(eval $(cmake-package))
