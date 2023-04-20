################################################################################
#
# kodi20-screensavers-rsxs
#
################################################################################

KODI20_SCREENSAVERS_RSXS_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVERS_RSXS_SITE = $(call github,xbmc,screensavers.rsxs,$(KODI20_SCREENSAVERS_RSXS_VERSION))
KODI20_SCREENSAVERS_RSXS_LICENSE = GPL-2.0+
KODI20_SCREENSAVERS_RSXS_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVERS_RSXS_DEPENDENCIES = bzip2 gli glm kodi20
KODI20_SCREENSAVERS_RSXS_CONF_OPTS = -DADDONS_TO_BUILD=screensavers.rsxs

$(eval $(cmake-package))
