################################################################################
#
# kodi-visualisation-waveform
#
################################################################################

KODI18_VISUALISATION_WAVEFORM_VERSION = 3.1.1-Leia
KODI18_VISUALISATION_WAVEFORM_SITE = $(call github,xbmc,visualization.waveform,$(KODI18_VISUALISATION_WAVEFORM_VERSION))
KODI18_VISUALISATION_WAVEFORM_LICENSE = GPL-2.0+
KODI18_VISUALISATION_WAVEFORM_LICENSE_FILES = COPYING
KODI18_VISUALISATION_WAVEFORM_DEPENDENCIES = kodi18

$(eval $(cmake-package))
