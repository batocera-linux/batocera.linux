################################################################################
#
# kodi20-visualisation-spectrum
#
################################################################################

KODI20_VISUALISATION_SPECTRUM_VERSION = 20.2.0-Nexus
KODI20_VISUALISATION_SPECTRUM_SITE = $(call github,xbmc,visualization.spectrum,$(KODI20_VISUALISATION_SPECTRUM_VERSION))
KODI20_VISUALISATION_SPECTRUM_LICENSE = GPL-2.0+
KODI20_VISUALISATION_SPECTRUM_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_SPECTRUM_DEPENDENCIES = glm kodi20

$(eval $(cmake-package))
