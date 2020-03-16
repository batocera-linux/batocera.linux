################################################################################
#
# kodi-visualisation-shadertoy
#
################################################################################

KODI18_VISUALISATION_SHADERTOY_VERSION = 1.2.3-Leia
KODI18_VISUALISATION_SHADERTOY_SITE = $(call github,xbmc,visualization.shadertoy,$(KODI18_VISUALISATION_SHADERTOY_VERSION))
KODI18_VISUALISATION_SHADERTOY_LICENSE = GPL-2.0+
KODI18_VISUALISATION_SHADERTOY_LICENSE_FILES = src/main.cpp
KODI18_VISUALISATION_SHADERTOY_DEPENDENCIES = glm kodi18 libplatform

$(eval $(cmake-package))
