
KODI_JOYSTICK_VERSION = 3c7ea5941495a958e9fa9b4877c3d726238e1a7b
KODI_JOYSTICK_SITE = $(call github,xbmc,peripheral.joystick,$(KODI_JOYSTICK_VERSION))
KODI_JOYSTICK_DEPENDENCIES = kodi-platform

$(eval $(cmake-package))
