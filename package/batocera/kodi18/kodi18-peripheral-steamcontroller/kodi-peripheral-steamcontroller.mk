################################################################################
#
# kodi-peripheral-steamcontroller
#
################################################################################

KODI18_PERIPHERAL_STEAMCONTROLLER_VERSION = 702fea828f9c5c94d0bd77dbb5fe78451edfa2ea
KODI18_PERIPHERAL_STEAMCONTROLLER_SITE = $(call github,kodi-game,peripheral.steamcontroller,$(KODI18_PERIPHERAL_STEAMCONTROLLER_VERSION))
KODI18_PERIPHERAL_STEAMCONTROLLER_LICENSE = GPL-2.0+
KODI18_PERIPHERAL_STEAMCONTROLLER_LICENSE_FILES = debian/copyright
KODI18_PERIPHERAL_STEAMCONTROLLER_DEPENDENCIES = kodi18-platform libusb

$(eval $(cmake-package))
