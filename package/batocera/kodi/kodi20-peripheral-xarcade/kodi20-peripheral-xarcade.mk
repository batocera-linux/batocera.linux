################################################################################
#
# kodi20-peripheral-xarcade
#
################################################################################

KODI20_PERIPHERAL_XARCADE_VERSION = 20.1.0-Nexus
KODI20_PERIPHERAL_XARCADE_SITE = $(call github,kodi-game,peripheral.xarcade,$(KODI20_PERIPHERAL_XARCADE_VERSION))
KODI20_PERIPHERAL_XARCADE_LICENSE = GPL-2.0+
KODI20_PERIPHERAL_XARCADE_LICENSE_FILES = LICENSE.md
KODI20_PERIPHERAL_XARCADE_DEPENDENCIES = kodi20

$(eval $(cmake-package))
