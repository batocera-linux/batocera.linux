################################################################################
#
# kodi-visualisation-goom
#
################################################################################

KODI18_VISUALISATION_GOOM_VERSION = 2.2.1-Leia
KODI18_VISUALISATION_GOOM_SITE = $(call github,xbmc,visualization.goom,$(KODI18_VISUALISATION_GOOM_VERSION))
KODI18_VISUALISATION_GOOM_LICENSE = GPL-2.0+
KODI18_VISUALISATION_GOOM_LICENSE_FILES = debian/copyright

KODI18_VISUALISATION_GOOM_DEPENDENCIES = glm kodi18

KODI18_VISUALISATION_GOOM_CONF_OPTS += \
	-DCMAKE_C_FLAGS="-std=c11"

$(eval $(cmake-package))
