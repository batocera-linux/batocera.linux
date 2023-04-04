################################################################################
#
# kodi20-visualisation-matrix
#
################################################################################

KODI20_VISUALISATION_MATRIX_VERSION = 20.2.0-Nexus
KODI20_VISUALISATION_MATRIX_SITE = $(call github,xbmc,visualization.matrix,$(KODI20_VISUALISATION_MATRIX_VERSION))
KODI20_VISUALISATION_MATRIX_LICENSE = GPL-2.0+
KODI20_VISUALISATION_MATRIX_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_MATRIX_DEPENDENCIES = glm kodi20

KODI20_VISUALISATION_MATRIX_CONF_OPTS = -DADDONS_TO_BUILD=visualization.matrix

$(eval $(cmake-package))
