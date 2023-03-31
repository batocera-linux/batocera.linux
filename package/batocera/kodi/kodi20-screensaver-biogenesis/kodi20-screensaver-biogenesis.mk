################################################################################
#
# kodi20-screensaver-biogenesis
#
################################################################################

KODI20_SCREENSAVER_BIOGENESIS_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_BIOGENESIS_SITE = $(call github,xbmc,screensaver.biogenesis,$(KODI20_SCREENSAVER_BIOGENESIS_VERSION))
KODI20_SCREENSAVER_BIOGENESIS_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_BIOGENESIS_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_BIOGENESIS_DEPENDENCIES = kodi20

$(eval $(cmake-package))
