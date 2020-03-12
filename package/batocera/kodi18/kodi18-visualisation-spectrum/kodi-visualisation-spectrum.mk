################################################################################
#
# kodi-visualisation-spectrum
#
################################################################################

KODI18_VISUALISATION_SPECTRUM_VERSION = 3.0.2-Leia
KODI18_VISUALISATION_SPECTRUM_SITE = $(call github,xbmc,visualization.spectrum,v$(KODI18_VISUALISATION_SPECTRUM_VERSION))
KODI18_VISUALISATION_SPECTRUM_LICENSE = GPL-2.0+
KODI18_VISUALISATION_SPECTRUM_LICENSE_FILES = COPYING
KODI18_VISUALISATION_SPECTRUM_DEPENDENCIES = kodi18

$(eval $(cmake-package))
