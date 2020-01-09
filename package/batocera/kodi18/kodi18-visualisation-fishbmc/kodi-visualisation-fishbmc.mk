################################################################################
#
# kodi-visualisation-fishbmc
#
################################################################################

KODI18_VISUALISATION_FISHBMC_VERSION = 5.1.2-Leia
KODI18_VISUALISATION_FISHBMC_SITE = $(call github,xbmc,visualization.fishbmc,$(KODI18_VISUALISATION_FISHBMC_VERSION))
KODI18_VISUALISATION_FISHBMC_LICENSE = GPL-2.0+
KODI18_VISUALISATION_FISHBMC_LICENSE_FILES = visualization.fishbmc/LICENSE
KODI18_VISUALISATION_FISHBMC_DEPENDENCIES = kodi18

$(eval $(cmake-package))
