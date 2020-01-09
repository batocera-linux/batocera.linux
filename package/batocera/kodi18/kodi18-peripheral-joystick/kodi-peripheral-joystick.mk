################################################################################
#
# kodi-peripheral-joystick
#
################################################################################

KODI18_PERIPHERAL_JOYSTICK_VERSION = 1.4.8-Leia
KODI18_PERIPHERAL_JOYSTICK_SITE = $(call github,xbmc,peripheral.joystick,$(KODI18_PERIPHERAL_JOYSTICK_VERSION))
KODI18_PERIPHERAL_JOYSTICK_LICENSE = GPL-2.0+
KODI18_PERIPHERAL_JOYSTICK_LICENSE_FILES = src/addon.cpp
KODI18_PERIPHERAL_JOYSTICK_DEPENDENCIES = kodi18 tinyxml udev

$(eval $(cmake-package))
