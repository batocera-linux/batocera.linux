################################################################################
#
# kodi20-visualisation-starburst
#
################################################################################

KODI20_VISUALISATION_STARBURST_VERSION = 20.2.0-Nexus
KODI20_VISUALISATION_STARBURST_SITE = $(call github,xbmc,visualization.starburst,$(KODI20_VISUALISATION_STARBURST_VERSION))
KODI20_VISUALISATION_STARBURST_LICENSE = GPL-2.0+
KODI20_VISUALISATION_STARBURST_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_STARBURST_DEPENDENCIES = glm kodi20

KODI20_VISUALISATION_STARBURST_CONF_OPTS = -DADDONS_TO_BUILD=visualization.starburst

$(eval $(cmake-package))
