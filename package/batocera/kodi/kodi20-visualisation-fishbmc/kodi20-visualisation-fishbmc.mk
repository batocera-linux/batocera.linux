################################################################################
#
# kodi20-visualisation-fishbmc
#
################################################################################

KODI20_VISUALISATION_FISHBMC_VERSION = 20.2.0-Nexus
KODI20_VISUALISATION_FISHBMC_SITE = $(call github,xbmc,visualization.fishbmc,$(KODI20_VISUALISATION_FISHBMC_VERSION))
KODI20_VISUALISATION_FISHBMC_LICENSE = GPL-2.0+
KODI20_VISUALISATION_FISHBMC_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_FISHBMC_DEPENDENCIES = glm kodi20

$(eval $(cmake-package))
