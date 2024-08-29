################################################################################
#
# kodi21-kodi-platform
#
################################################################################

KODI21_KODI_PLATFORM_VERSION = 809c5e9d711e378561440a896fcb7dbcd009eb3d
KODI21_KODI_PLATFORM_SITE = $(call github,xbmc,kodi-platform,$(KODI21_KODI_PLATFORM_VERSION))
KODI21_KODI_PLATFORM_LICENSE = GPL-2.0+
KODI21_KODI_PLATFORM_LICENSE_FILES = LICENSE.md
KODI21_KODI_PLATFORM_DEPENDENCIES = kodi21

$(eval $(cmake-package))
