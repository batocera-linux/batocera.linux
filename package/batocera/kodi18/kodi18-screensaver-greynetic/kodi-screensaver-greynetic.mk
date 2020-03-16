################################################################################
#
# kodi-screensaver-greynetic
#
################################################################################

KODI18_SCREENSAVER_GREYNETIC_VERSION = 2.2.2-Leia
KODI18_SCREENSAVER_GREYNETIC_SITE = $(call github,xbmc,screensaver.greynetic,$(KODI18_SCREENSAVER_GREYNETIC_VERSION))
KODI18_SCREENSAVER_GREYNETIC_LICENSE = GPL-2.0+
KODI18_SCREENSAVER_GREYNETIC_LICENSE_FILES = src/GreyNetic.cpp
KODI18_SCREENSAVER_GREYNETIC_DEPENDENCIES = kodi18

$(eval $(cmake-package))
