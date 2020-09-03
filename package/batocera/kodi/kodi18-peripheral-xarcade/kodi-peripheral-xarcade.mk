################################################################################
#
# kodi-peripheral-xarcade
#
################################################################################

KODI18_PERIPHERAL_XARCADE_VERSION = 51e1a4550a6c7d7feeb01760a731af17bea6c524
KODI18_PERIPHERAL_XARCADE_SITE = $(call github,kodi-game,peripheral.xarcade,$(KODI18_PERIPHERAL_XARCADE_VERSION))
KODI18_PERIPHERAL_XARCADE_LICENSE = GPL-2.0+
KODI18_PERIPHERAL_XARCADE_LICENSE_FILES = debian/copyright
KODI18_PERIPHERAL_XARCADE_DEPENDENCIES = kodi18

$(eval $(cmake-package))
