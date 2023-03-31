################################################################################
#
# kodi20-visualisation-waveform
#
################################################################################

KODI20_VISUALISATION_WAVEFORM_VERSION = 20.2.1-Nexus
KODI20_VISUALISATION_WAVEFORM_SITE = $(call github,xbmc,visualization.waveform,$(KODI20_VISUALISATION_WAVEFORM_VERSION))
KODI20_VISUALISATION_WAVEFORM_LICENSE = GPL-2.0+
KODI20_VISUALISATION_WAVEFORM_LICENSE_FILES = LICENSE.md
KODI20_VISUALISATION_WAVEFORM_DEPENDENCIES = glm kodi20

$(eval $(cmake-package))
