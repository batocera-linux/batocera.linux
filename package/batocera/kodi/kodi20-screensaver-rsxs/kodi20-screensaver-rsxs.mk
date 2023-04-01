################################################################################
#
# kodi20-screensaver-rsxs
#
################################################################################

KODI20_SCREENSAVER_RSXS_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_RSXS_SITE = $(call github,xbmc,screensavers.rsxs,$(KODI20_SCREENSAVER_RSXS_VERSION))
KODI20_SCREENSAVER_RSXS_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_RSXS_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_RSXS_DEPENDENCIES = bzip2 gli glm kodi20

$(eval $(cmake-package))
