################################################################################
#
# kodi20-visualisation-pictureit
#
################################################################################

KODI20_VISUALISATION_PICTUREIT_VERSION = 20.2.0-Nexus
KODI20_VISUALISATION_PICTUREIT_SITE = $(call github,xbmc,visualization.pictureit,$(KODI20_VISUALISATION_PICTUREIT_VERSION))
KODI20_VISUALISATION_PICTUREIT_LICENSE = GPL-2.0+
KODI20_VISUALISATION_PICTUREIT_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_PICTUREIT_DEPENDENCIES = glm kodi20

KODI20_VISUALISATION_PICTUREIT_CONF_OPTS = -DADDONS_TO_BUILD=visualization.pictureit

$(eval $(cmake-package))
