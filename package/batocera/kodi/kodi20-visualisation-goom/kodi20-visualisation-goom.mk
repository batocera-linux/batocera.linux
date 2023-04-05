################################################################################
#
# kodi20-visualisation-goom
#
################################################################################

KODI20_VISUALISATION_GOOM_VERSION = 20.1.1-Nexus
KODI20_VISUALISATION_GOOM_SITE = $(call github,xbmc,visualization.goom,$(KODI20_VISUALISATION_GOOM_VERSION))
KODI20_VISUALISATION_GOOM_LICENSE = GPL-2.0+
KODI20_VISUALISATION_GOOM_LICENSE_FILES = LICENSE.md

KODI20_VISUALISATION_GOOM_DEPENDENCIES = glm kodi20

KODI20_VISUALISATION_GOOM_CONF_OPTS += \
    -DADDONS_TO_BUILD=visualization.goom \
	-DCMAKE_C_FLAGS="-std=c11"

$(eval $(cmake-package))
