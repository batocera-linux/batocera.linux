################################################################################
#
# kodi-screensaver-matrixtrails
#
################################################################################

KODI18_SCREENSAVER_MATRIXTRAILS_VERSION = 2.2.1-Leia
KODI18_SCREENSAVER_MATRIXTRAILS_SITE = $(call github,xbmc,screensaver.matrixtrails,v$(KODI18_SCREENSAVER_MATRIXTRAILS_VERSION))
KODI18_SCREENSAVER_MATRIXTRAILS_LICENSE = GPL-2.0+
KODI18_SCREENSAVER_MATRIXTRAILS_LICENSE_FILES = src/matrixtrails.cpp
KODI18_SCREENSAVER_MATRIXTRAILS_DEPENDENCIES = kodi18 libsoil

$(eval $(cmake-package))
