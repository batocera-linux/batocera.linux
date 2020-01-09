################################################################################
#
# kodi-screensaver-rsxs
#
################################################################################

KODI18_SCREENSAVER_RSXS_VERSION = 7cb648507440d87948dec10d5bfdab3b722d37fe
KODI18_SCREENSAVER_RSXS_SITE = $(call github,xbmc,screensavers.rsxs,$(KODI18_SCREENSAVER_RSXS_VERSION))
KODI18_SCREENSAVER_RSXS_LICENSE = GPL-3.0
KODI18_SCREENSAVER_RSXS_DEPENDENCIES = bzip2 gli glm jpeg kodi18 libpng libtool tiff

$(eval $(cmake-package))
