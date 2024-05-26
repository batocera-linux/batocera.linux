################################################################################
#
# kodi20-p8-platform
#
################################################################################

KODI20_P8_PLATFORM_VERSION = cee64e9dc0b69e8d286dc170a78effaabfa09c44
KODI20_P8_PLATFORM_SITE = $(call github,xbmc,platform,$(KODI20_P8_PLATFORM_VERSION))
KODI20_P8_PLATFORM_LICENSE = GPL-2.0+
KODI20_P8_PLATFORM_LICENSE_FILES = LICENSE.md
KODI20_P8_PLATFORM_DEPENDENCIES = kodi20

$(eval $(cmake-package))
