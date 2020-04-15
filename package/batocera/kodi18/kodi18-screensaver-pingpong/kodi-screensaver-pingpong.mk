################################################################################
#
# kodi-screensaver-pingpong
#
################################################################################

KODI18_SCREENSAVER_PINGPONG_VERSION = 2.1.2-Leia
KODI18_SCREENSAVER_PINGPONG_SITE = $(call github,xbmc,screensaver.pingpong,$(KODI18_SCREENSAVER_PINGPONG_VERSION))
KODI18_SCREENSAVER_PINGPONG_LICENSE = GPL-2.0+
KODI18_SCREENSAVER_PINGPONG_LICENSE_FILES = src/readme.txt
KODI18_SCREENSAVER_PINGPONG_DEPENDENCIES = kodi18

$(eval $(cmake-package))
