################################################################################
#
# kodi20-visualisation-shadertoy
#
################################################################################

KODI20_VISUALISATION_SHADERTOY_VERSION = 20.3.0-Nexus
KODI20_VISUALISATION_SHADERTOY_SITE = $(call github,xbmc,visualization.shadertoy,$(KODI20_VISUALISATION_SHADERTOY_VERSION))
KODI20_VISUALISATION_SHADERTOY_LICENSE = GPL-2.0+
KODI20_VISUALISATION_SHADERTOY_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_SHADERTOY_DEPENDENCIES = glm jsoncpp kodi20

$(eval $(cmake-package))
