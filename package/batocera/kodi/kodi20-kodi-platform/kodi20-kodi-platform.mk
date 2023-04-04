################################################################################
#
# kodi20-kodi-platform
#
################################################################################

KODI20_KODI_PLATFORM_VERSION = 809c5e9d711e378561440a896fcb7dbcd009eb3d
KODI20_KODI_PLATFORM_SITE = $(call github,xbmc,kodi-platform,$(KODI20_KODI_PLATFORM_VERSION))
KODI20_KODI_PLATFORM_LICENSE = GPL-2.0+
KODI20_KODI_PLATFORM_LICENSE_FILES = LICENSE.md
KODI20_KODI_PLATFORM_DEPENDENCIES = kodi20

$(eval $(cmake-package))
