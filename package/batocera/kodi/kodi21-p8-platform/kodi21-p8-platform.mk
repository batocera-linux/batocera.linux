################################################################################
#
# kodi21-p8-platform
#
################################################################################

KODI21_P8_PLATFORM_VERSION = cee64e9dc0b69e8d286dc170a78effaabfa09c44
KODI21_P8_PLATFORM_SITE = $(call github,xbmc,platform,$(KODI21_P8_PLATFORM_VERSION))
KODI21_P8_PLATFORM_LICENSE = GPL-2.0+
KODI21_P8_PLATFORM_LICENSE_FILES = LICENSE.md
KODI21_P8_PLATFORM_DEPENDENCIES = kodi21

$(eval $(cmake-package))
