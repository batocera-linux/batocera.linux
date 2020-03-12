################################################################################
#
# kodi-peripheral-joystick
#
################################################################################

KODI18_PERIPHERAL_JOYSTICK_VERSION = 1.4.9-Leia
KODI18_PERIPHERAL_JOYSTICK_SITE = $(call github,xbmc,peripheral.joystick,$(KODI18_PERIPHERAL_JOYSTICK_VERSION))
KODI18_PERIPHERAL_JOYSTICK_LICENSE = GPL-2.0+
KODI18_PERIPHERAL_JOYSTICK_LICENSE_FILES = debian/copyright
KODI18_PERIPHERAL_JOYSTICK_DEPENDENCIES = kodi18 tinyxml udev

$(eval $(cmake-package))
