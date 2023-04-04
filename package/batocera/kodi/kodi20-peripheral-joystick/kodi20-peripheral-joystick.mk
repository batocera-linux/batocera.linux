################################################################################
#
# kodi20-peripheral-joystick
#
################################################################################

KODI20_PERIPHERAL_JOYSTICK_VERSION = 20.1.0-Nexus
KODI20_PERIPHERAL_JOYSTICK_SITE = $(call github,xbmc,peripheral.joystick,$(KODI20_PERIPHERAL_JOYSTICK_VERSION))
KODI20_PERIPHERAL_JOYSTICK_LICENSE = GPL-2.0+
KODI20_PERIPHERAL_JOYSTICK_LICENSE_FILES = LICENSE.md
KODI20_PERIPHERAL_JOYSTICK_DEPENDENCIES = kodi20 tinyxml udev

$(eval $(cmake-package))
