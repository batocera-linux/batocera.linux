################################################################################
#
# kodi20-visualisation-projectm
#
################################################################################

KODI20_VISUALISATION_PROJECTM_VERSION = 20.2.0-Nexus
KODI20_VISUALISATION_PROJECTM_SITE = $(call github,xbmc,visualization.projectm,$(KODI20_VISUALISATION_PROJECTM_VERSION))
KODI20_VISUALISATION_PROJECTM_LICENSE = GPL-2.0+
KODI20_VISUALISATION_PROJECTM_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_PROJECTM_DEPENDENCIES = glm kodi20 projectm

KODI20_VISUALISATION_PROJECTM_CONF_OPTS = -DADDONS_TO_BUILD=visualization.projectm

$(eval $(cmake-package))
