################################################################################
#
# kodi-visualisation-goom
#
################################################################################

KODI18_VISUALISATION_GOOM_VERSION = abd131a7a5780dee532da9bb1a6c192fbd3f6b89
KODI18_VISUALISATION_GOOM_SITE = $(call github,xbmc,visualization.goom,$(KODI18_VISUALISATION_GOOM_VERSION))
KODI18_VISUALISATION_GOOM_LICENSE = GPL-2.0+
KODI18_VISUALISATION_GOOM_LICENSE_FILES = src/Main.cpp

KODI18_VISUALISATION_GOOM_DEPENDENCIES = kodi18

$(eval $(cmake-package))
